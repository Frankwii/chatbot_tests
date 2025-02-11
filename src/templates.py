from __future__ import annotations
from pathlib import Path
from functools import reduce

import json
import re

class PromptTemplate():
    def __init__(self, template:str, placeholders:set[str]|None=None):
        self.__template=template
        if placeholders is None:
            self.__placeholders=self.__find_placeholders()
        else:
            self.__placeholders=placeholders

    def __find_placeholders(self):
        """
        Find all placeholders in a raw string using a regex.
        Valid placeholders contain only capital letters, numbers, underscores and whitespace
        """
        pattern=r"{([A-Z0-9_ ]+)}"
        return set(re.findall(pattern, self.__template))

    def __to_string(self)->str:
        """
        Casts a template to a string, checking whether any placeholders have been left out.
        """
        if not self.is_filled():
            print(f"WARNING: Casting a non-filled template to string. Remaining placeholders are the following: {self.__placeholders}")
        return self.__template

    def is_filled(self)->bool:
        """
        Returns True if all placeholders in the template have been replaced by actual text and False otherwise.
        """
        return not bool(self.__placeholders)

    def unsafe_replace_one(self, placeholder:str, content:str)->PromptTemplate:
        """
        Replaces all instances of the placeholder (if any) by the specified content.

        Args:
            - placeholder (str): The placeholder string, without the keys around it.
            Examples: "DATABASE SCHEMA", "HINT".
            - content (str): The string to be put in place of the placeholder

        Returns:
            - Template: Another Template object with the specified placeholder having been replaced.
        """
        new_template=self.__template.replace("{"+placeholder+"}", content)
        new_placeholders=self.__placeholders-{placeholder}

        return self.__class__(new_template, new_placeholders)

    def replace_one(self, placeholder:str, content:str)->PromptTemplate:
        """
        Replaces all instances of the placeholder by the specified content, but throws an error if the placeholder is not present in the template.

        Args:
            - placeholder (str): The placeholder string, without the keys around it.
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
        if not self.__placeholders.issubset(set(replacements.keys())):
            raise ValueError("Not enough placeholders specified.")
        return str(reduce(lambda template, replace_pair: template.unsafe_replace_one(*replace_pair), replacements.items(), self))

    def __str__(self)->str:
        return self.__to_string()

class PromptPreparer():
    def __init__(self, template_json_path:Path|str):
        with open(template_json_path, 'r', encoding='utf-8') as json_file:
            data=dict(json.load(json_file))

        self.__prompt_templates={prompt_name:PromptTemplate(raw_template) for prompt_name, raw_template in data.items()}

    def fill(self, template_name:str, replacements:dict[str,str]):
        return self.__prompt_templates[template_name].replace_all(replacements)
