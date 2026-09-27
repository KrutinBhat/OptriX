
"""
OptriX AI Intelligence Layer
Module: entity_resolution.py

Purpose:
    Normalize and consolidate likely duplicate entities across
    heterogeneous market research sources.

Supported entity categories:
    company, product, person, organization, location, unknown.

Design:
    - Deterministic entity identifiers.
    - Unicode-aware text normalization.
    - URL and domain normalization.
    - Exact and fuzzy matching.
    - Source provenance preservation.
    - Conservative entity merging.

This module does not claim that fuzzy matches are verified identities.
"""

from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_SIMILARITY_THRESHOLD = 0.90
MIN_NAME_LENGTH_FOR_FUZZY_MATCH = 6

ENTITY_CATEGORIES = {
    "company",
    "product",
    "person",
    "organization",
    "location",
    "unknown",
}

LEGAL_SUFFIXES = {
    "inc",
    "incorporated",
    "llc",
    "ltd",
    "limited",
    "llp",
    "private",
    "pvt",
    "corp",
    "corporation",
    "company",
    "co",
    "plc",
    "gmbh",
}


class EntityResolutionError(ValueError):
    """Raised for invalid entity-resolution inputs."""


@dataclass(slots=True)
class EntityMention:
    """One observed mention of an entity in a source record."""

    source: str
    original_name: str
    normalized_name: str
    url: str | None = None
    domain: str | None = None
    location: str | None = None
    record: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResolvedEntity:
    """Canonical entity with linked source mentions."""

    entity_id: str
    canonical_name: str
    normalized_name: str
    category: str
    domains: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    mentions: list[EntityMention] = field(default_factory=list)
    resolution_method: str = "exact"
    resolution_confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "canonical_name": self.canonical_name,
            "normalized_name": self.normalized_name,
            "category": self.category,
            "domains": list(self.domains),
            "locations": list(self.locations),
            "source_names": list(self.source_names),
            "mentions": [
                mention.to_dict()
                for mention in self.mentions
            ],
            "resolution_method": self.resolution_method,
            "resolution_confidence": self.resolution_confidence,
        }


class EntityResolver:
    """
    Resolve duplicate entities across research records.

    Parameters
    ----------
    similarity_threshold:
        Minimum SequenceMatcher similarity required for fuzzy matching.
        A higher value is more conservative.

    allow_fuzzy_matching:
        If False, only exact normalized names or exact domains match.
    """

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        allow_fuzzy_matching: bool = True,
    ) -> None:
        if (
            isinstance(similarity_threshold, bool)
            or not isinstance(similarity_threshold, (int, float))
            or not 0.70 <= float(similarity_threshold) <= 1.0
        ):
            raise EntityResolutionError(
                "similarity_threshold must be between 0.70 and 1.0."
            )

        self.similarity_threshold = float(
            similarity_threshold
        )
        self.allow_fuzzy_matching = bool(
            allow_fuzzy_matching
        )

    def resolve(
        self,
        records: Iterable[Mapping[str, Any]],
        source: str = "unknown",
        category: str = "unknown",
    ) -> list[ResolvedEntity]:
        """
        Resolve a collection of source records.

        Each record should contain at least one recognizable name
        field, such as title, name, company, or product.

        Records without a usable name are ignored and logged.
        """

        if isinstance(records, (str, bytes, Mapping)):
            raise EntityResolutionError(
                "records must be an iterable of mapping objects."
            )

        normalized_category = self._normalize_category(
            category
        )

        mentions: list[EntityMention] = []

        for record in records:
            if not isinstance(record, Mapping):
                logger.debug(
                    "Skipping non-mapping entity record."
                )
                continue

            mention = self._extract_mention(
                record=record,
                source=source,
            )

            if mention is not None:
                mentions.append(mention)

        entities: list[ResolvedEntity] = []

        for mention in mentions:
            match = self._find_match(
                mention=mention,
                entities=entities,
            )

            if match is None:
                entity = self._create_entity(
                    mention=mention,
                    category=normalized_category,
                )

                entities.append(entity)

            else:
                self._merge_mention(
                    entity=match[0],
                    mention=mention,
                    method=match[1],
                    confidence=match[2],
                )

        logger.info(
            "Entity resolution completed: %d mentions, %d entities.",
            len(mentions),
            len(entities),
        )

        return entities

    def resolve_sources(
        self,
        research_data: Mapping[str, Any],
        category: str = "unknown",
    ) -> list[ResolvedEntity]:
        """
        Resolve records from a normalized multi-source payload.

        Expected input:
            {
                "search": {"results": [...]},
                "maps": {"results": [...]},
                ...
            }
        """

        if not isinstance(research_data, Mapping):
            raise EntityResolutionError(
                "research_data must be a mapping."
            )

        all_records: list[EntityMention] = []

        for source_name, source_data in research_data.items():
            if not isinstance(source_data, Mapping):
                continue

            results = source_data.get("results", [])

            if not isinstance(results, list):
                continue

            for record in results:
                if not isinstance(record, Mapping):
                    continue

                mention = self._extract_mention(
                    record=record,
                    source=str(source_name),
                )

                if mention is not None:
                    all_records.append(mention)

        entities: list[ResolvedEntity] = []

        for mention in all_records:
            match = self._find_match(
                mention=mention,
                entities=entities,
            )

            if match is None:
                entities.append(
                    self._create_entity(
                        mention=mention,
                        category=self._normalize_category(
                            category
                        ),
                    )
                )
            else:
                self._merge_mention(
                    entity=match[0],
                    mention=mention,
                    method=match[1],
                    confidence=match[2],
                )

        return entities

    # ---------------------------------------------------------------
    # MENTION EXTRACTION
    # ---------------------------------------------------------------

    @classmethod
    def _extract_mention(
        cls,
        record: Mapping[str, Any],
        source: str,
    ) -> EntityMention | None:
        """Extract a normalized entity mention from a raw record."""

        name = cls._first_text(
            record,
            (
                "name",
                "company",
                "company_name",
                "business_name",
                "product_name",
                "title",
                "brand",
            ),
        )

        if not name:
            return None

        url = cls._first_text(
            record,
            (
                "link",
                "url",
                "website",
                "website_url",
            ),
        )

        domain = cls._normalize_domain(url)

        location = cls._first_text(
            record,
            (
                "address",
                "location",
                "city",
                "region",
            ),
        )

        return EntityMention(
            source=str(source),
            original_name=name,
            normalized_name=cls.normalize_name(name),
            url=url,
            domain=domain,
            location=location,
            record=dict(record),
        )

    @staticmethod
    def _first_text(
        record: Mapping[str, Any],
        fields: tuple[str, ...],
    ) -> str | None:
        """Return the first non-empty string in the given fields."""

        for field_name in fields:
            value = record.get(field_name)

            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    # ---------------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------------

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a name for entity comparison.

        Legal suffixes are removed only from the comparison form.
        The original display name remains unchanged.
        """

        if not isinstance(name, str):
            raise EntityResolutionError(
                "Entity name must be a string."
            )

        value = unicodedata.normalize(
            "NFKD",
            name,
        )

        value = "".join(
            char
            for char in value
            if not unicodedata.combining(char)
        )

        value = value.casefold()
        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        tokens = value.split()

        while tokens and tokens[-1] in LEGAL_SUFFIXES:
            tokens.pop()

        return " ".join(tokens)

    @staticmethod
    def _normalize_domain(
        url: str | None,
    ) -> str | None:
        """Extract a normalized domain from a URL."""

        if not isinstance(url, str) or not url.strip():
            return None

        candidate = url.strip()

        if "://" not in candidate:
            candidate = "https://" + candidate

        try:
            parsed = urlparse(candidate)
            hostname = parsed.hostname

        except ValueError:
            return None

        if not hostname:
            return None

        hostname = hostname.casefold().strip(".")

        hostname = hostname.removeprefix("www.")

        return hostname or None

    @staticmethod
    def _normalize_category(
        category: str,
    ) -> str:
        if not isinstance(category, str):
            return "unknown"

        normalized = category.strip().lower()

        if normalized not in ENTITY_CATEGORIES:
            return "unknown"

        return normalized

    # ---------------------------------------------------------------
    # MATCHING
    # ---------------------------------------------------------------

    def _find_match(
        self,
        mention: EntityMention,
        entities: list[ResolvedEntity],
    ) -> tuple[ResolvedEntity, str, float] | None:
        """
        Find a likely matching entity.

        Exact domain matches are preferred. Exact normalized names
        are next. Fuzzy matching is only used when enabled.
        """

        # 1. Exact domain match.
        if mention.domain:
            for entity in entities:
                if mention.domain in entity.domains:
                    return entity, "exact_domain", 1.0

        # 2. Exact normalized name match.
        for entity in entities:
            if (
                mention.normalized_name
                and mention.normalized_name
                == entity.normalized_name
            ):
                return entity, "exact_name", 1.0

        # 3. Conservative fuzzy matching.
        if not self.allow_fuzzy_matching:
            return None

        if (
            len(mention.normalized_name)
            < MIN_NAME_LENGTH_FOR_FUZZY_MATCH
        ):
            return None

        best_match: (
            tuple[ResolvedEntity, str, float] | None
        ) = None

        best_similarity = 0.0

        for entity in entities:
            if (
                len(entity.normalized_name)
                < MIN_NAME_LENGTH_FOR_FUZZY_MATCH
            ):
                continue

            similarity = SequenceMatcher(
                None,
                mention.normalized_name,
                entity.normalized_name,
            ).ratio()

            if similarity < self.similarity_threshold:
                continue

            # If both records have different explicit domains,
            # do not merge them based only on similar names.
            if (
                mention.domain
                and entity.domains
                and mention.domain not in entity.domains
            ):
                continue

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (
                    entity,
                    "fuzzy_name",
                    round(similarity, 4),
                )

        return best_match

    # ---------------------------------------------------------------
    # ENTITY CREATION AND MERGING
    # ---------------------------------------------------------------

    @classmethod
    def _create_entity(
        cls,
        mention: EntityMention,
        category: str,
    ) -> ResolvedEntity:
        """Create a new canonical entity."""

        entity_id = cls._make_entity_id(
            mention.normalized_name,
            mention.domain,
        )

        return ResolvedEntity(
            entity_id=entity_id,
            canonical_name=mention.original_name,
            normalized_name=mention.normalized_name,
            category=category,
            domains=(
                [mention.domain]
                if mention.domain
                else []
            ),
            locations=(
                [mention.location]
                if mention.location
                else []
            ),
            source_names=[mention.source],
            mentions=[mention],
            resolution_method="initial",
            resolution_confidence=1.0,
        )

    @staticmethod
    def _merge_mention(
        entity: ResolvedEntity,
        mention: EntityMention,
        method: str,
        confidence: float,
    ) -> None:
        """Attach a mention while preserving provenance."""

        entity.mentions.append(mention)

        if (
            mention.domain
            and mention.domain not in entity.domains
        ):
            entity.domains.append(mention.domain)

        if (
            mention.location
            and mention.location not in entity.locations
        ):
            entity.locations.append(mention.location)

        if mention.source not in entity.source_names:
            entity.source_names.append(mention.source)

        # Prefer an original name that contains more information.
        if len(mention.original_name) > len(
            entity.canonical_name
        ):
            entity.canonical_name = mention.original_name

        if confidence < entity.resolution_confidence:
            entity.resolution_confidence = confidence
            entity.resolution_method = method

    @staticmethod
    def _make_entity_id(
        normalized_name: str,
        domain: str | None,
    ) -> str:
        """Generate a stable, non-sensitive entity identifier."""

        identity = domain or normalized_name

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:16]

        return f"ent_{digest}"


def resolve_entities(
    records: Iterable[Mapping[str, Any]],
    source: str = "unknown",
    category: str = "unknown",
) -> list[dict[str, Any]]:
    """Convenience function returning serializable entities."""

    resolver = EntityResolver()

    entities = resolver.resolve(
        records=records,
        source=source,
        category=category,
    )

    return [
        entity.to_dict()
        for entity in entities
    ]