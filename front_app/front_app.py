"""
# My first app
Here's our first attempt at using data to create a table:
"""

import asyncio
import json
import math
import os
import time
import streamlit as st
from sh import tail

from utils import (get_test_list_from_file, post_request, get_local_ip,
                   waiting_for_file, delete_result_file)
from settings import (ROW_NUMBER, TESTS_RESULT_FILE,
                      ANDROID_TESTS_LIST_FILE, IOS_TESTS_LIST_FILE,
                      START_QR_CODE_FILE)
from qr_code_tasks import make_qr
from back_app.tasks.initialisation_tasks import get_internal_order


if 'qr_code_filename' not in st.session_state:
    st.session_state['qr_code_filename'] = START_QR_CODE_FILE

if 'current_order_id' not in st.session_state:
    st.session_state['current_order_id'] = None

if "checkbox" not in st.session_state:
    st.session_state["checkbox"] = False

if "tests_list" not in st.session_state:
    st.session_state["tests_list"] = []

if "select_tests_label" not in st.session_state:
    st.session_state["select_tests_label"] = ""

if "run_tests_status" not in st.session_state:
    st.session_state["run_tests_status"] = True

st.set_page_config(layout='wide')

st.header('The RMQ test stand')

if st.button("Start new session"):
    response = asyncio.run(post_request(
        f"http://{get_local_ip()}:8001/api/v1/start-session",
    ))
    if response[0] == 200:
        current_order_id = json.loads(response[1])["data"]
        # time.sleep(20)
        timer = time.time()
        counter = 0
        current_order = get_internal_order(current_order_id)
        while current_order.get("queue_code", None) is None and (time.time() - timer) < 20:
            current_order = get_internal_order(current_order_id)
            counter += 1
            # print(counter)
            time.sleep(0.1)
        print(time.time() - timer)
        st.session_state['qr_code_filename'] = make_qr(str({"queue_code": current_order["queue_code"]}))
        st.session_state['current_order_id'] = current_order_id
        st.session_state["run_tests_status"] = False

st.image(
    st.session_state['qr_code_filename'],
    caption="QR-code includes 5 sign code to connect to RMQ",
    width=200)

col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    if st.button("Select Android tests"):
        st.session_state["tests_list"] = asyncio.run(get_test_list_from_file(ANDROID_TESTS_LIST_FILE))
        st.session_state["select_tests_label"] = "Android tests"
    x = st.empty()
    x.info(st.session_state["select_tests_label"])

with col2:
    if st.button("Select Ios tests"):
        st.session_state["tests_list"] = asyncio.run(get_test_list_from_file(IOS_TESTS_LIST_FILE))
        st.session_state["select_tests_label"] = "Ios tests"
        x.info(st.session_state["select_tests_label"])
with col3:
    if st.button("Select All"):
        st.session_state["checkbox"] = True
with col4:
    if st.button("Deselect All"):
        st.session_state["checkbox"] = False

tests_list = st.session_state["tests_list"]

checkbox_agree_list = []
column_number = math.ceil(len(tests_list)/ROW_NUMBER)
if column_number != 0:
    columns_list = st.columns(column_number, gap="large")
    i = 0
    for column in columns_list:
        with column:
            j = 0
            while j <= (ROW_NUMBER - 1) and i < len(tests_list):
                checkbox_agree_list.append({"test": tests_list[i], "condition": st.checkbox(tests_list[i]["test_name"], value=st.session_state["checkbox"])})
                i += 1
                j += 1

delete_result_file(f"temp/{TESTS_RESULT_FILE}{st.session_state['current_order_id']}.log")

repeat_number = st.slider(
    "Insert a number of repeatting",
    min_value=1,
    max_value=50,
    step=1,
    disabled=st.session_state["run_tests_status"]
)
choosed_test_list = []
if st.button("Run tests", disabled=st.session_state["run_tests_status"]):
    params = {
        "current_order_id": st.session_state['current_order_id']
    }
    if checkbox_agree_list:
        for test in checkbox_agree_list:
            if test["condition"]:
                for _ in range(0, repeat_number):
                    choosed_test_list.append(test["test"])
        response = asyncio.run(post_request(
            f"http://{get_local_ip()}:8001/api/v1/start-test-list",
            json_data=choosed_test_list,
            params=params))
        st.write(response)
        if response[0] == 200:
            asyncio.run(waiting_for_file(f"temp/{TESTS_RESULT_FILE}{st.session_state['current_order_id']}.log"))
            with open(f"temp/{TESTS_RESULT_FILE}{st.session_state['current_order_id']}.log", encoding='utf-8') as file:
                for line in tail("-f", f"temp/{TESTS_RESULT_FILE}{st.session_state['current_order_id']}.log", _iter=True):
                    st.text(line)
        else:
            st.write("Error of calling /api/v1/start-test-list")
    else:
        st.session_state["select_tests_label"] = "You need to choose a tests set"
        x.info(st.session_state["select_tests_label"])
