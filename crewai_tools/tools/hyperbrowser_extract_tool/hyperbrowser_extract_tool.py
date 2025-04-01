from typing import TYPE_CHECKING, Any, List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CreateSessionParams,
        ExtractJobResponse,
        StartExtractJobParams,
    )


try:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CreateSessionParams,
        ExtractJobResponse,
        StartExtractJobParams,
    )

    HYPERBROWSER_AVAILABLE = True
except ImportError:
    HYPERBROWSER_AVAILABLE = False


class HyperbrowserExtractTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Hyperbrowser web extract tool"
    description: str = (
        "Extract data from webpages using Hyperbrowser and return the results"
    )
    args_schema: Type[BaseModel] = StartExtractJobParams
    api_key: Optional[str] = None
    _hyperbrowser: Optional["Hyperbrowser"] = PrivateAttr(None)

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._initialize_hyperbrowser()

    def _initialize_hyperbrowser(self) -> None:
        try:
            if HYPERBROWSER_AVAILABLE:
                self._hyperbrowser = Hyperbrowser(api_key=self.api_key)
            else:
                raise ImportError
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'hyperbrowser' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "hyperbrowser"], check=True)
                    from hyperbrowser import Hyperbrowser

                    self._hyperbrowser = Hyperbrowser(api_key=self.api_key)
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install hyperbrowser package")
            else:
                raise ImportError(
                    "`hyperbrowser` package not found, please run `uv add hyperbrowser`"
                )

    def _run(
        self,
        urls: List[str],
        system_prompt: Optional[str] = None,
        prompt: Optional[str] = None,
        schema_: Optional[Any] = None,
        wait_for: Optional[int] = None,
        session_options: Optional[CreateSessionParams] = None,
        max_links: Optional[int] = None,
    ) -> ExtractJobResponse:
        if not self._hyperbrowser:
            raise RuntimeError("Hyperbrowser not properly initialized")

        return self._hyperbrowser.extract.start_and_wait(
            StartExtractJobParams(
                urls=urls,
                system_prompt=system_prompt,
                prompt=prompt,
                schema_=schema_,
                wait_for=wait_for,
                session_options=session_options,
                max_links=max_links,
            )
        )
