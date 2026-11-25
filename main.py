# Use streamlit for the frontend since this is pretty simple code. Doesn't need a complex frontend
import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate("admin-key.json"))
    return firestore.client()

@st.cache_data
def get_data_format():
    # Using the first entry in the sample data as the example to build the form off of
    return {
    "id": "req_01WVNY7YZ0",
    "conversationId": "conv_008200",
    "userId": "user_0087",
    "timestamp": datetime.now(),
    "model": {
      "provider": "Anthropic",
      "name": "claude-haiku-5-5",
      "region": "us-west-2"
    },
    "conversation": {
      "turn": 1,
      "ageSeconds": 0
    },
    "tokens": {
      "input": 1413,
      "cachedInput": 0,
      "output": 477,
      "reasoning": 0,
      "total": 1890
    },
    "performance": {
      "ttftMs": 449,
      "generationMs": 2540,
      "totalLatencyMs": 3006,
      "tokensPerSecond": 187.8
    },
    "tools": [
      {
        "name": "code_interpreter",
        "durationMs": 209,
        "status": "success"
      }
    ],
    "request": {
      "temperature": 0.7,
      "streaming": True
    },
    "result": {
      "status": "success",
      "finishReason": "stop"
    },
    "cost": {
      "inputUsd": 0.0014,
      "outputUsd": 0.0024,
      "totalUsd": 0.0038
    }
  }

db = get_db()
st.title("LLM Info Interface")

chats = db.collection("chats")

# create & update
with st.form("dynamic_create", enter_to_submit=False):
    data = get_data_format()
    # Using a loop by key types here so I don't have to manually create the whole form.
    # The same loop by key type is done for dictionary values
    for outer_key in data.keys():
        match(data[outer_key]):
            # will match timestamp
            case datetime():
                value = st.datetime_input(f"{outer_key}", key=outer_key)
                data[outer_key] = value
            # matches the first few fields
            case str():
                value = st.text_input(f"{outer_key}", key=outer_key, placeholder=f"{data[outer_key]}")
                data[outer_key] = value
            # every other field is a dictionary with subfields
            # except for tools, which is a list handled in the form below
            case dict():
                st.text(outer_key)
                for inner_key in data[outer_key].keys():
                    match(data[outer_key][inner_key]):
                        case bool():
                            value = st.checkbox(f"{inner_key}", key=f"{outer_key}.{inner_key}")
                            data[outer_key][inner_key] = value
                        case int():
                            value = st.number_input(f"{inner_key}", min_value=0, key=f"{outer_key}.{inner_key}")
                            data[outer_key][inner_key] = value
                        case float():
                            value = st.number_input(f"{inner_key}", min_value=0.0000, key=f"{outer_key}.{inner_key}")
                            data[outer_key][inner_key] = value
                        case str():
                            value = st.text_input(f"{inner_key}", key=f"{outer_key}.{inner_key}", placeholder=f"{data[outer_key][inner_key]}")
                            data[outer_key][inner_key] = value                

    submitted = st.form_submit_button("Submit")

# tools is a list containing dictionaries. I'm using another form to add tools to a list.
# This has the drawback of not being able to remove specific tools from the list.
# This needs to stay across session states otherwise it is reset every time a button is clicked
if "tools_list" not in st.session_state:
    st.session_state.tools_list = []

with st.form("tool_form", enter_to_submit=False):
    st.text("tools")
    name = st.text_input("name", key="tool_name", placeholder="code_interpreter")
    duration = st.number_input("durationMs", min_value=0, key="tool_duration")
    status = st.text_input("status", key="tool_status", placeholder="success")

    add_tool = st.form_submit_button("Add tool")
    clear_tools = st.form_submit_button("Clear added tools")

if add_tool:
    st.session_state.tools_list.append({"name": name, "durationMs": duration, "status": status})
    st.success("Tool added")

if clear_tools:
    st.session_state.tools_list = []
    st.info("Cleared tools")

if submitted:
    # Put the tools list in if we've submitted
    data["tools"] = st.session_state.tools_list

    # Hacky data overwriting - data["performance"]["ttftMs"] should be null
    # if data["request"]["streaming"] is false.
    # Overwrite the user's ttftMs value if this condition is true.
    # Pretty ugly; this is a cost of not hardcoding the whole form.
    if not data["request"]["streaming"]:
        data["performance"]["ttftMs"] = None

    # Get the id out of the data we're submitting since it's the key
    filtered = {k: v for k, v in data.items() if k != 'id'}

    # This works for both create and update. If the key matches existing data, set() will update that data.
    # If the key is new, set() will create the entry.
    chats.document(data["id"]).set(filtered)

    st.success("Submitted data")

    # Clear the tools list
    st.session_state.tools_list = []

# delete
with st.form("delete_form", enter_to_submit=False):
    del_id = st.text_input("Remove by ID", placeholder="id")
    deleted = st.form_submit_button("Delete")

if deleted:
    del_doc = chats.document(del_id)
    if del_doc.get().exists:
        chats.document(del_id).delete()
        st.success(f"Deleted entry with id {del_id}")
    else:
        st.error(f"Error: no entry found matching id {del_id}")

# read
# Display as a dataframe instead of a table because it is more interactive
# and looks better when displaying a larger amount of data like this.
st.dataframe([{"id": d.id, **d.to_dict()} for d in chats.stream()])
