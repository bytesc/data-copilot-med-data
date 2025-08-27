import json
from typing import List, Tuple, Optional, Dict, Union

import pandas as pd
from matplotlib import pyplot as plt

from agent.utils.llm_access.LLM import get_llm
from .copilot.examples.path_tools import generate_img_path
from .llm_analysis.llm_predict_hdb import llm_predict_hdb_func, get_llm_predict_hdb_info

from .tools_def import engine, STATIC_URL

llm = get_llm()



# def get_minimap(lat_lng_list: Optional[List[Tuple[float, float]]] = None,
#                 postcode_list: Optional[List[str]] = None) -> str:
#     """
#     get_minimap(lat_lng_list: Optional[List[Tuple[float, float]]] = None, postcode_list: Optional[List[str]] = None) -> str:
#     Generate an HTML iframe for a minimap with optional markers in latitude and longitude pairs or or postal codes.
#     Returns an HTML iframe string.
#
#     The function creates an HTML iframe that embeds a minimap from OneMap.sg.
#     Users can specify a list of latitude and longitude pairs or postal codes
#     to be marked on the map.
#
#     Args:
#     - lat_lng_list (Optional[List[Tuple[float, float]]]): A list of tuples,
#       where each tuple contains a latitude and longitude pair for a marker.
#       Default is None.
#     - postcode_list (Optional[List[str]]): A list of postal codes to be marked
#       on the map. Default is None.
#
#     Returns:
#     - str: An HTML iframe string that can be embedded in a webpage to display
#       the minimap with the specified markers.
#
#     Example usage:
#     ```python
#     get_minimap_func(lat_lng_list=[(1.2996492424497, 103.8447478575), (1.29963489170907, 103.845842317726)])
#     get_minimap_func(postcode_list=["123456"])
#     ```
#
#     """
#     html = get_minimap_func(lat_lng_list, postcode_list)
#     return html

