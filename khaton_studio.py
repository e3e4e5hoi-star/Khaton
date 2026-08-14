"""Khaton Studio frozen-app entrypoint."""
import khaton  # noqa: F401
import khaton.bytecode  # noqa: F401
import khaton.lexer  # noqa: F401
import khaton.parser  # noqa: F401
import khaton.runtime  # noqa: F401

from studio.khaton_studio import main

if __name__ == "__main__":
    main()
