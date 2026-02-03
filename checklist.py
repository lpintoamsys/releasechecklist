import streamlit as st
import json
import os
import csv
import io

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Package Creation Checklist",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# Custom CSS for Professional Styling
# --------------------------------------------------
st.markdown(
    """
<style>
    /* Main container styling */
    .main {
        padding: 1rem 1.5rem;
    }

    /* Title styling */
    h1 {
        color: #1f77b4;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    h2 {
        color: #2c3e50;
        font-size: 1.1rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.2rem;
    }
    h3 {
        color: #34495e;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    /* Button styling */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        padding: 0.3rem 1rem;
        border: none;
        border-radius: 6px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.08);
    }
    .stButton > button:hover {
        background-color: #0d47a1;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.13);
    }

    /* Download button styling */
    .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        font-weight: 600;
        padding: 0.3rem 1rem;
        border: none;
        border-radius: 6px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        background-color: #218838;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.13);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f7f8fa;
        border-radius: 6px;
        border-left: 3px solid #1f77b4;
        font-weight: 600;
        color: #2c3e50;
        font-size: 1rem;
        padding: 0.3rem 0.7rem;
        margin-bottom: 0.2rem;
    }

    /* Input fields styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #d0d5dd;
        border-radius: 6px;
        padding: 0.3rem;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.08);
    }

    /* Selectbox styling */
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid #d0d5dd;
        font-size: 0.95rem;
        padding: 0.2rem 0.5rem;
    }

    /* Checklist card styling */
    .stExpander {
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.07);
        margin-bottom: 0.5rem;
        padding: 0.2rem 0.7rem;
    }

    /* Status badges */
    .status-yes {
        color: #155724;
        background: #e6f4ea;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-no {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Info box styling */
    .stInfo {
        background-color: #e3f2fd;
        border: 1px solid #1f77b4;
        border-radius: 6px;
        padding: 0.7rem;
        color: #0d47a1;
        font-size: 0.95rem;
    }

    /* Divider styling */
    hr {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }

    /* Column styling */
    .task-header {
        background: linear-gradient(135deg, #1f77b4 0%, #2196F3 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

JSON_FILE = "checklist.json"

DEFAULT_STRUCTURE = {
    "Windows": {"items": [], "automated": {}, "task_ids": {}, "descriptions": {}},
    "Linux": {"items": [], "automated": {}, "task_ids": {}, "descriptions": {}},
}


# --------------------------------------------------
# Load JSON with auto-migration + self-healing
# --------------------------------------------------
def load_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Resetting file.")
                return DEFAULT_STRUCTURE.copy()
    else:
        return DEFAULT_STRUCTURE.copy()

    # 🔄 MIGRATION: Old structure with Full/Diff → Simplified
    if "Full" in data.get("Windows", {}) or "Diff" in data.get("Windows", {}):
        new_data = {
            "Windows": {"items": [], "automated": {}},
            "Linux": {"items": [], "automated": {}},
        }
        for os_name in ["Windows", "Linux"]:
            if os_name in data:
                for pkg in ["Full", "Diff"]:
                    if pkg in data[os_name]:
                        new_data[os_name]["items"].extend(
                            data[os_name][pkg].get("items", [])
                        )
                        new_data[os_name]["automated"].update(
                            data[os_name][pkg].get("automated", {})
                        )
        data = new_data

    # 🛠 Self-healing structure
    for os_name in ["Windows", "Linux"]:
        data.setdefault(
            os_name, {"items": [], "automated": {}, "task_ids": {}, "descriptions": {}}
        )
        data[os_name].setdefault("automated", {})
        data[os_name].setdefault("task_ids", {})
        data[os_name].setdefault("descriptions", {})

        # Remove duplicates
        data[os_name]["items"] = list(dict.fromkeys(data[os_name]["items"]))

        # Add missing entries
        for item in data[os_name]["items"]:
            data[os_name]["automated"].setdefault(item, False)
            data[os_name]["task_ids"].setdefault(item, "")
            data[os_name]["descriptions"].setdefault(item, "")

    return data


# --------------------------------------------------
# Save JSON
# --------------------------------------------------
def save_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --------------------------------------------------
# Generate CSV
# --------------------------------------------------
def generate_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["OS", "Task ID", "Item", "Description", "Automated"])

    for os_name in ["Windows", "Linux"]:
        items = data[os_name]["items"]
        automated = data[os_name].get("automated", {})
        task_ids = data[os_name].get("task_ids", {})
        descriptions = data[os_name].get("descriptions", {})

        for item in items:
            auto_status = "Yes" if automated.get(item, False) else "No"
            task_id = task_ids.get(item, "")
            description = descriptions.get(item, "")
            writer.writerow([os_name, task_id, item, description, auto_status])

    return output.getvalue()


# --------------------------------------------------
# Load data on startup
# --------------------------------------------------
if "data" not in st.session_state:
    st.session_state.data = load_json()

data = st.session_state.data

# --------------------------------------------------
# ✅ UPDATED HEADER WITH TEAM LINE + REALTIME IST DATE/TIME
# --------------------------------------------------
st.markdown(
    """
<div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #8a9cff 0%, #a87dcc 100%); \
            border-radius: 10px; margin-bottom: 1.8rem; color: white;'>
    <h2 style='margin: 0; font-size: 1.8rem; color: white; border-bottom: none;'>
        🚀 DevOps Quality Initiative
    </h2>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📦 Package Creation Checklist")


# --------------------------------------------------
# Product and OS selection
# --------------------------------------------------
PRODUCTS = [k for k in data.keys() if k not in ("Windows", "Linux")]
DEFAULT_PRODUCT = "CI"
DEFAULT_OS = "Windows"

if "product_selected" not in st.session_state:
    st.session_state.product_selected = DEFAULT_PRODUCT
if "os_selected" not in st.session_state:
    st.session_state.os_selected = DEFAULT_OS

product_selected = st.selectbox(
    "Select Product",
    PRODUCTS,
    index=PRODUCTS.index(st.session_state.product_selected)
    if st.session_state.product_selected in PRODUCTS
    else 0,
)

os_selected = st.selectbox(
    "Select OS",
    ["Windows", "Linux"],
    index=0 if st.session_state.os_selected == "Windows" else 1,
)

st.session_state.product_selected = product_selected
st.session_state.os_selected = os_selected

items = data[product_selected][os_selected]["items"]
automated = data[product_selected][os_selected].get("automated", {})
task_ids = data[product_selected][os_selected].get("task_ids", {})
descriptions = data[product_selected][os_selected].get("descriptions", {})

st.markdown("### ➕ Add New Item")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    new_task_id = st.text_input("Task ID (optional)", placeholder="e.g., TASK-031")

with col2:
    new_item = st.text_input("Task Title", placeholder="Enter checklist item...")

with col3:
    new_automated = st.checkbox(
        "Automated?",
        value=False,
        help="Check if this item is automated, leave unchecked for manual.",
    )

new_description = st.text_area(
    "Description (optional)",
    placeholder="Enter validation steps or notes...",
    height=100,
)

add_clicked = st.button("Add Item", use_container_width=True)

if add_clicked:
    if new_item.strip():
        if new_item not in items:
            items.append(new_item)
            automated[new_item] = new_automated
            task_ids[new_item] = new_task_id.strip()
            descriptions[new_item] = new_description.strip()

            save_json(data)
            st.success("✅ Item added successfully")
            st.rerun()
        else:
            st.warning("⚠️ Item already exists")
    else:
        st.warning("⚠️ Task title cannot be empty")


def format_description(desc):
    if not desc:
        return ""
    import re
    return re.sub(r"(\d+)\.\s+", r"\n\1. ", desc).strip()


if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if items:
    st.markdown("### 📋 Checklist Items")

    for idx, item in enumerate(items):
        task_id = task_ids.get(item, "")
        desc = descriptions.get(item, "")

        header_text = f"{task_id} - {item}" if task_id else item
        status_badge = (
            f'<span class="status-yes">✓ Automated</span>'
            if automated.get(item, False)
            else f'<span class="status-no">○ Manual</span>'
        )

        with st.expander(f"🔹 {header_text}", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                if task_id:
                    st.markdown(f"**Task ID:** `{task_id}`")
                st.markdown(f"**Item:** {item}")

            with col2:
                st.markdown("**Status:**")
                st.markdown(status_badge, unsafe_allow_html=True)

            with col3:
                pass

            if desc.strip():
                st.markdown("---")
                st.markdown("**Description:**")
                st.markdown(format_description(desc))

    st.markdown("### ✏️ Manage Items")
    col_edit, col_delete = st.columns(2)

    with col_edit:
        edit_options = [
            f"{task_ids.get(item, '')} - {item}" if task_ids.get(item, "") else item
            for item in items
        ]
        selected_display = st.selectbox("Select item to edit", edit_options)
        selected_item = items[edit_options.index(selected_display)]
        if st.button("✏️ Edit Selected Item", use_container_width=True):
            st.session_state.edit_index = items.index(selected_item)

    with col_delete:
        delete_item = st.selectbox("Select item to delete", items, key="delete_select")
        if st.button("🗑️ Delete Selected Item", use_container_width=True):
            removed = items.pop(items.index(delete_item))
            automated.pop(removed, None)
            task_ids.pop(removed, None)
            descriptions.pop(removed, None)

            save_json(data)
            st.rerun()

    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        if idx < len(items):
            item = items[idx]
            st.markdown("---")
            st.markdown("### 📝 Edit Item Details")

            updated_task_id = st.text_input(
                "Task ID (optional)",
                value=task_ids.get(item, ""),
                key=f"taskidbox_{idx}",
            )

            updated_text = st.text_input("Item name", value=item, key=f"editbox_{idx}")

            updated_description = st.text_area(
                "Description (optional)",
                value=descriptions.get(item, ""),
                key=f"descbox_{idx}",
                height=100,
            )

            updated_automated = st.checkbox(
                "Automated (check if automated, uncheck for manual)",
                value=automated.get(item, False),
                key=f"automatedbox_{idx}",
            )

            col_save, col_cancel = st.columns(2)

            with col_save:
                if st.button("💾 Save Changes", key=f"save_{idx}", use_container_width=True):
                    old_item_name = items[idx]
                    new_item_name = updated_text.strip() if updated_text else old_item_name

                    items[idx] = new_item_name

                    if old_item_name != new_item_name:
                        automated[new_item_name] = automated.pop(old_item_name, False)
                        task_ids[new_item_name] = task_ids.pop(old_item_name, "")
                        descriptions[new_item_name] = descriptions.pop(old_item_name, "")

                    task_ids[new_item_name] = updated_task_id.strip() if updated_task_id else ""
                    descriptions[new_item_name] = updated_description.strip() if updated_description else ""
                    automated[new_item_name] = updated_automated

                    save_json(data)

                    st.session_state.edit_index = None
                    st.success("✅ Changes saved successfully")
                    st.rerun()

            with col_cancel:
                if st.button("❌ Cancel", key=f"cancel_{idx}", use_container_width=True):
                    st.session_state.edit_index = None
                    st.rerun()

else:
    st.info("No checklist items available")

# --------------------------------------------------
# Export to CSV
# --------------------------------------------------
st.divider()
st.markdown("### 📥 Export Checklist")

col1, col2 = st.columns(2)

with col1:
    csv_data = generate_csv(data)
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="release_checklist.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    if st.button("📋 Copy CSV to Clipboard", use_container_width=True):
        st.write("CSV data ready to copy:")
        st.code(csv_data, language="csv")
