from dataclasses import dataclass, field
from typing import Type, Any, List, Dict, Optional


@dataclass
class EntityConfig:
    slug: str
    display_name: str
    module: str
    import_sequence: int
    model: Type[Any]
    serializer_class: Optional[Type[Any]] = None
    description: str = ""
    supports_import: bool = True
    supports_export: bool = True
    required_fields: List[str] = field(default_factory=list)


class EntityRegistry:
    _registry: Dict[str, EntityConfig] = {}

    @classmethod
    def register(cls, config: EntityConfig):
        cls._registry[config.slug] = config

    @classmethod
    def get(cls, slug: str) -> EntityConfig:
        if slug not in cls._registry:
            raise KeyError(f'Entity not registered: {slug}')
        return cls._registry[slug]

    @classmethod
    def all(cls) -> List[EntityConfig]:
        return sorted(cls._registry.values(), key=lambda e: e.import_sequence)

    @classmethod
    def by_module(cls, module: str) -> List[EntityConfig]:
        return [e for e in cls.all() if e.module == module]

    @classmethod
    def modules(cls) -> List[str]:
        seen = []
        for e in cls.all():
            if e.module not in seen:
                seen.append(e.module)
        return seen
