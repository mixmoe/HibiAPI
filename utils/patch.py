# flake8:noqa:F405
from pydantic.schema import *  # type:ignore


def field_singleton_schema(  # type:ignore
    field: ModelField,
    *,
    by_alias: bool,
    model_name_map: Dict[TypeModelOrEnum, str],
    ref_template: str,
    schema_overrides: bool = False,
    ref_prefix: Optional[str] = None,
    known_models: TypeModelSet,
) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str]]:
    """
    This function is indirectly used by ``field_schema()``, you should probably be using that function.

    Take a single Pydantic ``ModelField``, and return its schema and any additional definitions from sub-models.
    """
    from pydantic.main import BaseModel

    definitions: Dict[str, Any] = {}
    nested_models: Set[str] = set()
    if field.sub_fields:
        return field_singleton_sub_fields_schema(
            field.sub_fields,
            by_alias=by_alias,
            model_name_map=model_name_map,
            schema_overrides=schema_overrides,
            ref_prefix=ref_prefix,
            ref_template=ref_template,
            known_models=known_models,
        )
    if field.type_ is Any or field.type_.__class__ == TypeVar:
        return {}, definitions, nested_models  # no restrictions
    if is_callable_type(field.type_):
        raise SkipField(
            f"Callable {field.name} was excluded from schema since JSON schema has no equivalent type."
        )
    f_schema: Dict[str, Any] = {}
    if field.field_info is not None and field.field_info.const:
        f_schema["const"] = field.default
    field_type = field.type_
    if is_literal_type(field_type):
        values = literal_values(field_type)
        if len(values) > 1:
            return field_schema(
                multivalue_literal_field_for_schema(values, field),
                by_alias=by_alias,
                model_name_map=model_name_map,
                ref_prefix=ref_prefix,
                ref_template=ref_template,
                known_models=known_models,
            )
        literal_value = values[0]
        field_type = literal_value.__class__
        f_schema["const"] = literal_value

    if lenient_issubclass(field_type, Enum):
        # NOTE: this part is different from the original PyDantic due to Enum class parsing issue
        # Reference: https://github.com/samuelcolvin/pydantic/issues/1857
        enum_name = model_name_map.get(field_type, normalize_name(field_type.__name__))
        f_schema, schema_overrides = get_field_info_schema(field)
        f_schema.update(
            get_schema_ref(enum_name, ref_prefix, ref_template, schema_overrides)
        )
        definitions[enum_name] = enum_process_schema(field_type)
    else:
        add_field_type_to_schema(field_type, f_schema)

        modify_schema = getattr(field_type, "__modify_schema__", None)
        if modify_schema:
            modify_schema(f_schema)

    if f_schema:
        return f_schema, definitions, nested_models

    # Handle dataclass-based models
    if lenient_issubclass(getattr(field_type, "__pydantic_model__", None), BaseModel):
        field_type = field_type.__pydantic_model__

    if issubclass(field_type, BaseModel):
        model_name = model_name_map[field_type]
        if field_type not in known_models:
            sub_schema, sub_definitions, sub_nested_models = model_process_schema(
                field_type,
                by_alias=by_alias,
                model_name_map=model_name_map,
                ref_prefix=ref_prefix,
                ref_template=ref_template,
                known_models=known_models,
            )
            definitions.update(sub_definitions)
            definitions[model_name] = sub_schema
            nested_models.update(sub_nested_models)
        else:
            nested_models.add(model_name)
        schema_ref = get_schema_ref(
            model_name, ref_prefix, ref_template, schema_overrides
        )
        return schema_ref, definitions, nested_models

    raise ValueError(f"Value not declarable with JSON Schema, field: {field}")


from pydantic import schema as _pydantic_schema

from .log import logger

_pydantic_schema.field_singleton_schema = field_singleton_schema

logger.debug("Monkeypatch for pydantic function <r>field_singleton_schema</r> applied")
