from abc import ABC, abstractmethod
from crewai import Agent as CrewAgent
from typing import Dict, Any
from pydantic import BaseModel, Field

class Agent(CrewAgent):
    def __init__(self, config):
        super().__init__(
            name=self.__class__.__name__,
            role="AI Trading Agent",
            goal="Execute trading operations",
            backstory="Expert in cryptocurrency trading",
            allow_delegation=False
        )
        self.config = config
        self._debug = False
        self._mock = False

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value

    @property
    def mock(self):
        return self._mock

    @mock.setter
    def mock(self, value: bool):
        self._mock = value

    def set_debug(self, debug: bool):
        self.debug = debug

    def set_mock(self, mock: bool):
        self.mock = mock

    def log(self, message):
        """Common logging method for all agents"""
        print(f"[{self.name}] {message}") 