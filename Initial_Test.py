import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# # 1. Define the unique identifiers from your original URL
SHEET_ID = "100Ert_y9Y5OrxzoBsmvvkH1xMjqiuUqBSIUS9jQbDr8"
GID = "1096843083" # This is the specific tab/sheet you want to read

# 2. Construct the direct CSV export URL
# We replace the '/edit...' part of the original URL with '/export?format=csv&gid='
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# 3. Read the data directly into a DataFrame
try:
    df_radar = pd.read_csv(url)

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure the spreadsheet's sharing setting is set to 'Anyone with the link can view.'")

# The variable 'df' now holds your pandas DataFrame


# --- 1. Data Loading & Comprehensive Cleaning ---
# Define the efficient replacement dictionary
responder_mapping = {
    "Someone who has worked as Richard's peer": "Peer view",
    "Someone who reports/reported to Richard - either directly or indirectly": "Subordinate view",
    "Someone who has managed Richard": "Manager view",
    "Me - Richard":"My view"
}

# Apply all replacements
df_radar['Responder'] = df_radar['Responder'].replace(responder_mapping)

# Clean Group and Score
df_radar['Group'] = df_radar['Group'].str.strip() 
df_radar['Score'] = pd.to_numeric(df_radar['Score'], errors='coerce')
df_radar.dropna(subset=['Score'], inplace=True)

# --- 2. Aggregation and Filtering ---
df_agg = df_radar.groupby(['Group', 'Responder'])['Score'].mean().reset_index()

# Define Chart Groups
groups_1 = ['Coaching', 'Innovation', 'Role Modelling', 'Vision']
groups_2 = ['Seeing the Big Picture', 'Listening to Everyone', 'Managing Stress', 'Handing Responsibility to the Team']

# Data for Chart 1 & 2 (Excluding 'Me - Richard')
df_agg_no_me = df_agg[df_agg['Responder'] != 'My view']

# Data for Chart 3 & 4 (Comparing 'Subordinate view' and 'Me - Richard')
comp_responders = ['Subordinate view', 'My view']
df_agg_comp = df_agg[df_agg['Responder'].isin(comp_responders)]


# --- 3. Define Updated Radar Chart Function (Unwrapped Labels) ---
def create_radar_chart_from_pivot(df_pivot, title, file_prefix):
    """
    Creates a radar chart from a pivoted DataFrame with unwrapped labels.
    """
    categories = df_pivot.index.tolist()
    N = len(categories)

    if N < 3:
        print(f"Skipping radar chart '{title}': Only {N} categories found. Need at least 3.")
        return None
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1] 

    # Use a larger figure size for more room
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True)) # Increased figure size
    ax.set_title(title, size=16, y=1.05, weight='bold')

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Plot lines
    for col in df_pivot.columns:
        values = df_pivot[col].values.flatten().tolist()
        values = [v if pd.notna(v) else 0 for v in values] 
        values += values[:1] 
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=col)
        ax.fill(angles, values, alpha=0.1)

    # Set the labels for the axes (categories/groups)
    ax.set_xticks(angles[:-1])
    
    # FIX 1: Use original categories (unwrapped)
    unwrapped_categories = categories 

    # FIX 2: Clear default labels and manually place text farther out
    ax.set_xticklabels([]) # Clear default labels first

    # FIX 3: Increased radial position to 8.0 for unwrapped text safety
    radial_pos = 5.3
    
    for label, angle in zip(unwrapped_categories, angles):
                   
        # Determine horizontal alignment
        ha = 'left' if 0 < angle < np.pi else 'right'
        if angle == 0 or angle == np.pi:
            ha = 'center'
        
        # Adjust position slightly based on angle and set label properties
        ax.text(
            angle, 
            radial_pos,
            label, 
            size=10, 
            horizontalalignment=ha, 
            verticalalignment='center'
        )

    # Set the y-axis limits (Scores 1-5)
    ax.set_rlabel_position(0)
    ax.set_yticks(np.arange(1, 6))
    ax.set_yticklabels([str(i) for i in np.arange(1, 6)], color="grey", size=10)
    ax.set_ylim(0, 5)

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.0, 1.05), fontsize=9)

    # Save the chart
    file_name = f'{file_prefix}_radar_chart_unwrapped.png' 
    plt.savefig(file_name, bbox_inches='tight')
    plt.show()
    plt.close()
    return file_name


# --- 4. Generate Radar Charts ---
chart_files = []

# --- Chart 1: Strategic Groups (Excluding 'Me - Richard') ---
df_pivot_1_filtered = df_agg_no_me[df_agg_no_me['Group'].isin(groups_1)].pivot(index='Group', columns='Responder', values='Score')
chart_1_file = create_radar_chart_from_pivot(
    df_pivot_1_filtered, 
    'Transformational Leadership View' \
    '', 
    'radar_strategic_no_me_unwrapped'
)
chart_files.append(chart_1_file)

# --- Chart 2: Operational Groups (Excluding 'Me - Richard') ---
df_pivot_2_filtered = df_agg_no_me[df_agg_no_me['Group'].isin(groups_2)].pivot(index='Group', columns='Responder', values='Score')
chart_2_file = create_radar_chart_from_pivot(
    df_pivot_2_filtered, 
    'Adaptive Leadership View', 
    'radar_operational_no_me_unwrapped'
)
chart_files.append(chart_2_file)

# --- Chart 3: Strategic Groups (Subordinate vs. Self) ---
df_pivot_3_comp = df_agg_comp[df_agg_comp['Group'].isin(groups_1)].pivot(index='Group', columns='Responder', values='Score')
chart_3_file = create_radar_chart_from_pivot(
    df_pivot_3_comp, 
    'Transformational Leadership: Subordinate View vs. Self-Assessment', 
    'radar_strategic_sub_vs_me_unwrapped'
)
chart_files.append(chart_3_file)

# --- Chart 4: Operational Groups (Subordinate vs. Self) ---
df_pivot_4_comp = df_agg_comp[df_agg_comp['Group'].isin(groups_2)].pivot(index='Group', columns='Responder', values='Score')
chart_4_file = create_radar_chart_from_pivot(
    df_pivot_4_comp, 
    'Adaptive Leadership: Subordinate View vs. Self-Assessment', 
    'radar_operational_sub_vs_me_unwrapped'
)
chart_files.append(chart_4_file)

print(f"Successfully generated {len(chart_files)} radar charts with unwrapped labels.")