from __future__ import annotations

from klippyai_agent._compat import export_legacy_environment

export_legacy_environment()

from klipperai_agent.__main__ import main  # noqa: E402

__all__ = ["main"]


if __name__ == "__main__":
    main()
