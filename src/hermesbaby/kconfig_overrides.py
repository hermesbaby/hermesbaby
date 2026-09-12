import os

CFG_CONFIG_PRELOADED_MARKER = "HERMESBABY_CONFIG_PRELOADED"


def apply_kconfig_env_overrides(kconfig, prefix: str = "CONFIG_") -> None:
    for symbol_name, symbol in kconfig.syms.items():
        env_key = f"{prefix}{symbol_name}"
        env_value = os.environ.get(env_key)
        if env_value is None:
            continue
        symbol.set_value(env_value)


def export_kconfig_to_env(kconfig, prefix: str = "CONFIG_") -> None:
    for symbol_name, symbol in kconfig.syms.items():
        os.environ[f"{prefix}{symbol_name}"] = symbol.str_value
