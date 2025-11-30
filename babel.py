from fastapi_babel import Babel, BabelConfigs

configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="ar",
    BABEL_TRANSLATION_DIRECTORY="locales",
)
babel = Babel(
    configs=configs,
)
# pybabel compile -d locales

if __name__ == "__main__":
    babel.run_cli()
