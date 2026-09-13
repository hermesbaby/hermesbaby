import os
from dataclasses import dataclass

CFG_CONFIG_PRELOADED_MARKER = "HERMESBABY_CONFIG_PRELOADED"


def apply_kconfig_env_overrides(kconfig, prefix: str = "CONFIG_") -> None:
    for symbol_name, symbol in kconfig.syms.items():
        env_key = f"{prefix}{symbol_name}"
        env_value = os.environ.get(env_key)
        if env_value is None:
            continue
        symbol.set_value(env_value)


def export_kconfig_to_env(kconfig, prefix: str = "CONFIG_", target_env=None) -> None:
    if target_env is None:
        target_env = os.environ
    for symbol_name, symbol in kconfig.syms.items():
        target_env[f"{prefix}{symbol_name}"] = symbol.str_value


@dataclass
class ConfigSymbol:
    str_value: str
    visibility: bool = True


@dataclass
class ConfigCompat:
    syms: dict


def build_config_compat_from_env(prefix: str = "CONFIG_") -> ConfigCompat:
    syms = {}
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        symbol_name = env_key[len(prefix):]
        syms[symbol_name] = ConfigSymbol(str_value=env_value)
    return ConfigCompat(syms=syms)
