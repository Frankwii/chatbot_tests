from __future__ import annotations
from functools import reduce
from abc import ABC, abstractmethod
from collections import Counter
import warnings

import re

class Template(ABC):
    def __init__(self, text:str, placeholder_counts:dict[str, int]|None=None):
        self.__text=text
        if placeholder_counts is None:
            self.__placeholder_counts=self.__find_placeholders_and_counts()
        else:
            self.__placeholder_counts=placeholder_counts

        self.__placeholders=self.__placeholder_counts.keys()

    @staticmethod
    @abstractmethod
    def _format_placeholder_for_replacing(placeholder:str)->str:
        """
        Takes a placeholder and formats it into the string that should be replaced inside the text. It will be called using str.replace(_, self.__text).
        Child classes should implement this method. 
        """
        pass

    @property
    @abstractmethod
    def _placeholder_match_pattern(self)->str:
        """
        The regex to be used to match placeholders. It should contain a single capture group which will be the placeholder itself.
        Child classes should define this attribute.
        """
        pass

    def __find_placeholders_and_counts(self)->dict[str,int]:
        return dict(Counter(self.__find_all_placeholders()))

    def __find_all_placeholders(self)->list[str]:
        """
        Find all placeholders in the text according to the match pattern specified by the subclass.
        """
        return re.findall(self._placeholder_match_pattern, self.__text)

    def __to_string(self)->str:
        """
        Casts a template to a string, checking whether any placeholders have been left out.
        """
        if not self.is_filled():
            warnings.warn(f"Casting an unfilled template to a string. Remaining placeholders are the following: {self.__placeholders}")
        return self.__text

    def is_filled(self)->bool:
        """
        Returns True if all placeholders in the template have been replaced by actual text and False otherwise.
        """
        return not bool(self.__placeholder_counts)

    def unsafe_replace_one(self, placeholder_to_replace:str, content:str)->Template:
        """
        Replaces all instances of the placeholder (if any) by the specified content.

        Args:
            - placeholder (str): The placeholder string.
            Examples: "DATABASE SCHEMA", "HINT".
            - content (str): The string to be put in place of the placeholder

        Returns:
            - Template: Another Template object with the specified placeholder having been replaced.
        """
        new_text=self.__text.replace(self._format_placeholder_for_replacing(placeholder_to_replace), content)
        new_placeholder_counts={placeholder:count for placeholder, count in self.__placeholder_counts.items() if placeholder!=placeholder_to_replace}

        return self.__class__(new_text, new_placeholder_counts)

    def replace_one(self, placeholder:str, content:str)->Template:
        """
        Replaces all instances of the placeholder by the specified content, but throws an error if the placeholder is not present in the template.

        Args:
            - placeholder (str): The placeholder string.
            Examples: "DATABASE SCHEMA", "HINT".
            - content (str): The string to be put in place of the placeholder

        Returns:
            - Template: Another Template object with the specified placeholder having been replaced.

        Raises:
            - ValueError: If the specified placeholder cannot be found in the template.
        """
        if placeholder not in self.__placeholders:
            raise ValueError("Placeholder not found when trying to replace it.")
        return self.unsafe_replace_one(placeholder, content)

    def replace_all(self, replacements:dict[str,str])->str:
        """
        Replaces all placeholders in a template with the specified contents.

        Args:
            - replacements (dict[str, str]): A dictionary mapping each placeholder to its replacement string. Every placeholder defined in the template must have a corresponding key in this dictionary.

        Returns:
            - str: A new string where all placeholders have been replaced by their corresponding values.

        Raises:
            - ValueError: If the keys in the replacements dictionary do not contain the set of placeholders expected by the template.
        """
        if not set(self.__placeholders).issubset(set(replacements.keys())):
            raise ValueError("Not enough placeholders specified.")
        return str(reduce(lambda template, replace_pair: template.unsafe_replace_one(*replace_pair), replacements.items(), self))

    def count_placeholders(self)->int:
        return sum(self.__placeholder_counts.values())

    def count_unique_placeholders(self)->int:
        return len(self.__placeholders)

    def __str__(self)->str:
        return self.__to_string()

    def __repr__(self)->str:
        return f"{self.__class__.__name__} with the following placeholders and number of appearances: {self.__placeholder_counts}."

class PromptTemplate(Template):
    @staticmethod
    def _format_placeholder_for_replacing(placeholder:str)->str:
        """
        Placeholders are surrounded by braces.
        """
        return "{"+placeholder+"}"

    @property
    def _placeholder_match_pattern(self)->str:
        """
        Valid placeholders contain only capital letters, numbers, underscores and whitespace
        """
        return r"{([A-Z0-9_ ]+)}"
