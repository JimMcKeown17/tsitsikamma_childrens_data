import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import openpyxl

file_path = "20240801 Children's database - June Assessments - Main - School Anonymized.xlsx"
sheet_name = "Main"
children_orig = pd.read_excel(file_path, sheet_name=sheet_name)

def convert_to_int_or_blank(value):
    try:
        return int(value)
    except ValueError:
        return np.nan

def standardize_scores(df, max_scores, month):
    for skill, max_score in max_scores.items():
        column = f"{month} - {skill}"
        if column in df.columns:
            df[column] = (df[column] / max_score) * 10
    return df

def orig_copies(df, columns):
    for column in columns:
        df[column + " - Actual"] = df[column]
    return df


numeric_columns = ['Jan - Letter Sounds', 'Jan - Story Comprehension', 'Jan - Listen First Sound',
                   'Jan - Listen Words', 'Jan - Writing Letters', 'Jan - Read Words', 'Jan - Read Sentences',
                   'Jan - Read Story', 'Jan - Write CVCs', 'Jan - Write Sentences', 'Jan - Write Story',
                   '2024 Total Sessions', 'June - Letter Sounds', 'June - Story Comprehension',
                   'June - Listen First Sound',
                   'June - Listen Words', 'June - Writing Letters', 'June - Read Words', 'June - Read Sentences',
                   'June - Read Story', 'June - Write CVCs', 'June - Write Sentences', 'June - Write Story']

for column in numeric_columns:
    children_orig[column] = pd.to_numeric(children_orig[column], errors='coerce')

# Apply the function to the DataFrames
children_orig = orig_copies(children_orig, numeric_columns)

children = children_orig.copy()
# English scores dictionary
max_scores_english = {
    'Letter Sounds': 60,
    'Story Comprehension': 5,
    'Listen First Sound': 10,
    'Listen Words': 8,
    'Writing Letters': 26,
    'Read Words': 40,
    'Read Sentences': 20,
    'Read Story': 80,
    'Write CVCs': 12,
    'Write Sentences': 15,
    'Write Story': 16
}

# isiXhosa scores dictionary
max_scores_xhosa = {
    'Letter Sounds': 60,
    'Story Comprehension': 5,
    'Listen First Sound': 10,
    'Listen Words': 8,
    'Writing Letters': 26,
    'Read Words': 40,
    'Read Sentences': 5,  # Corrected for June
    'Read Story': 45,
    'Write CVCs': 12,  # Corrected for June
    'Write Sentences': 15,  # Check this for June
    'Write Story': 16
}

def apply_standardization(df, months, max_scores_english, max_scores_xhosa):
    df['Language'] = df['Language'].str.strip()  # Ensure no leading/trailing whitespaces
    for month in months:
        df = df.groupby('Language', group_keys=False).apply(
            lambda x: standardize_scores(x.copy(), max_scores_english if x.name == 'English' else max_scores_xhosa,
                                         month)
        )
    return df

# List of months to standardize
months = ['Jan', 'June']

# Apply the standardization function to each month
children = apply_standardization(children, months, max_scores_english, max_scores_xhosa)

children['On The Programme'] = children['2024 On Programme'].apply(
    lambda x: 'Yes' if x in ['Yes', 'Graduated'] else 'No')
children['On The Programme June'] = children['2024 Total Sessions'] > 5

children['LC Name'] = children['Current LC']
children['Schools'] = children['School']

def calculate_literacy_scores(children, month):
    children[f'{month} - Total'] = children[[f'{month} - Letter Sounds',
                                             f'{month} - Story Comprehension',
                                             f'{month} - Listen First Sound',
                                             f'{month} - Listen Words',
                                             f'{month} - Writing Letters',
                                             f'{month} - Read Words',
                                             f'{month} - Read Sentences',
                                             f'{month} - Read Story',
                                             f'{month} - Write CVCs',
                                             f'{month} - Write Sentences',
                                             f'{month} - Write Story']].sum(axis=1, min_count=1)

    children[f'{month} - Total - Actual'] = children[[f'{month} - Letter Sounds - Actual',
                                                      f'{month} - Story Comprehension - Actual',
                                                      f'{month} - Listen First Sound - Actual',
                                                      f'{month} - Listen Words - Actual',
                                                      f'{month} - Writing Letters - Actual',
                                                      f'{month} - Read Words - Actual',
                                                      f'{month} - Read Sentences - Actual',
                                                      f'{month} - Read Story - Actual',
                                                      f'{month} - Write CVCs - Actual',
                                                      f'{month} - Write Sentences - Actual',
                                                      f'{month} - Write Story - Actual']].sum(axis=1, min_count=1)

    children[f'{month} - Total Literacy Score'] = (0.05 * children[f'{month} - Letter Sounds'] +
                                                   0.05 * children[f'{month} - Story Comprehension'] +
                                                   0.05 * children[f'{month} - Listen First Sound'] +
                                                   0.05 * children[f'{month} - Listen Words'] +
                                                   0.05 * children[f'{month} - Writing Letters'] +
                                                   0.15 * children[f'{month} - Read Words'] +
                                                   0.1 * children[f'{month} - Read Sentences'] +
                                                   0.25 * children[f'{month} - Read Story'] +
                                                   0.05 * children[f'{month} - Write CVCs'] +
                                                   0.1 * children[f'{month} - Write Sentences'] +
                                                   0.1 * children[f'{month} - Write Story']
                                                   ) * 10

    children[f'{month} - GR Literacy Score'] = (0.3 * children[f'{month} - Letter Sounds'] +
                                                0.15 * children[f'{month} - Story Comprehension'] +
                                                0.15 * children[f'{month} - Listen First Sound'] +
                                                0.15 * children[f'{month} - Listen Words'] +
                                                0.25 * children[f'{month} - Writing Letters']
                                                ) * 10

    children[f'{month} - G1 Literacy Score'] = (0.1 * children[f'{month} - Letter Sounds'] +
                                                0.05 * children[f'{month} - Story Comprehension'] +
                                                0.05 * children[f'{month} - Listen First Sound'] +
                                                0.05 * children[f'{month} - Listen Words'] +
                                                0.2 * children[f'{month} - Writing Letters'] +
                                                0.15 * children[f'{month} - Read Words'] +
                                                0.15 * children[f'{month} - Read Sentences'] +
                                                0.1 * children[f'{month} - Read Story'] +
                                                0.1 * children[f'{month} - Write CVCs']
                                                ) * 10

    children[f'{month} - G2 Literacy Score'] = (0.05 * children[f'{month} - Letter Sounds'] +
                                                0.05 * children[f'{month} - Writing Letters'] +
                                                0.1 * children[f'{month} - Read Words'] +
                                                0.1 * children[f'{month} - Read Sentences'] +
                                                0.35 * children[f'{month} - Read Story'] +
                                                0.05 * children[f'{month} - Write CVCs'] +
                                                0.1 * children[f'{month} - Write Sentences'] +
                                                0.2 * children[f'{month} - Write Story']
                                                ) * 10

    return children

children_orig = calculate_literacy_scores(children_orig, 'Jan')
children = calculate_literacy_scores(children, 'Jan')
children_orig = calculate_literacy_scores(children_orig, 'June')
children = calculate_literacy_scores(children, 'June')

# Improvement Columns

children["June - Letter Sounds Improvement - Actual"] = children["June - Letter Sounds - Actual"] - children[
    "Jan - Letter Sounds - Actual"]
children["June - Story Comprehension Improvement - Actual"] = children["June - Story Comprehension - Actual"] - \
                                                              children["Jan - Story Comprehension - Actual"]
children["June - Listen First Sound Improvement - Actual"] = children["June - Listen First Sound - Actual"] - \
                                                             children["Jan - Listen First Sound - Actual"]
children["June - Listen Words Improvement - Actual"] = children["June - Listen Words - Actual"] - children[
    "Jan - Listen Words - Actual"]
children["June - Writing Letters Improvement - Actual"] = children["June - Writing Letters - Actual"] - children[
    "Jan - Writing Letters - Actual"]
children["June - Read Words Improvement - Actual"] = children["June - Read Words - Actual"] - children[
    "Jan - Read Words - Actual"]
children['June - Write CVCs Improvement - Actual'] = children['June - Write CVCs - Actual'] - children[
    'Jan - Write CVCs - Actual']
children['June - Write Sentences Improvement - Actual'] = children['June - Write Sentences - Actual'] - children[
    'Jan - Write Sentences - Actual']
children['June - Write Story Improvement - Actual'] = children['June - Write Story - Actual'] - children[
    'Jan - Write Story - Actual']
children['June - Total Improvement - Actual'] = children['June - Total - Actual'] - children['Jan - Total - Actual']

children["June - Letter Sounds Improvement"] = children["June - Letter Sounds"] - children["Jan - Letter Sounds"]
children["June - Story Comprehension Improvement"] = children["June - Story Comprehension"] - children[
    "Jan - Story Comprehension"]
children["June - Listen First Sound Improvement"] = children["June - Listen First Sound"] - children[
    "Jan - Listen First Sound"]
children["June - Listen Words Improvement"] = children["June - Listen Words"] - children["Jan - Listen Words"]
children["June - Writing Letters Improvement"] = children["June - Writing Letters"] - children[
    "Jan - Writing Letters"]
children["June - Read Words Improvement"] = children["June - Read Words"] - children["Jan - Read Words"]
children['June - Write CVCs Improvement'] = children['June - Write CVCs'] - children['Jan - Write CVCs']
children['June - Write Sentences Improvement'] = children['June - Write Sentences'] - children[
    'Jan - Write Sentences']
children['June - Write Story Improvement'] = children['June - Write Story'] - children['Jan - Write Story']
children['June - GR Literacy Score Improvement'] = children['June - GR Literacy Score'] - children[
    'June - GR Literacy Score']
children['June - Total Literacy Score Improvement'] = children['June - Total Literacy Score'] - children[
    'Jan - Total Literacy Score']
children['June - Total Improvement'] = children['June - Total'] - children['Jan - Total']

ecd = children[children['Grade'] == 'PreR']
primary = children[children['Grade'] != 'PreR']
GradeR = children[children['Grade'] == 'Grade R']
Grade1 = children[children['Grade'] == 'Grade 1']
Grade2 = children[children['Grade'] == 'Grade 2']
Grade3 = children[children['Grade'] == 'Grade 3']

##### STREAMLIT CODE BELOW #####
st.set_page_config(layout="wide")

st.image("Data site banners-24b.jpg")

# SCHOOL IMPROVEMENT COMPARING SCHOOLS

st.header("School Improvement Comparisons")
st.info("Clarkson children very good progress relative to most of Masi's schools. Especially considering the challenges rural area schools face. The Grade R's did excellent, which is really important for the future. The ECDCs did terrible.")

metric_choice = st.selectbox('Select an Assessment:', ('Standard', 'Raw Data'))

if metric_choice == 'Standard':
    metric = 'June - Total Literacy Score Improvement'
else:
    metric = 'June - Total Improvement - Actual'

grade_choice = st.selectbox('Select a Grade:', ('ECD', 'Grade R', 'Grade 1', 'Grade 2', 'Grade 3'), index=1)

if grade_choice == 'ECD':
    filtered_df = children[children['Grade'] == 'PreR']
else:
    filtered_df = children[children['Grade'] == grade_choice]

mean_scores = filtered_df.groupby('School')[metric].mean().reset_index()

# Define custom color mapping
custom_colors = {'Bambino': 'orange', 'Clarkson': 'orange', 'Vukani Day Care': 'orange'}

# Define custom color mapping
custom_colors = {'Bambino': 'feature', 'Clarkson': 'feature', 'Vukani Day Care': 'feature'}

# Apply custom colors
mean_scores['color'] = mean_scores['School'].apply(lambda x: custom_colors.get(x, 'control'))

fig = px.bar(mean_scores,
             x='School',
             y=metric,
             title=f'{metric} by School',
             labels={metric: 'Mean Literacy Score', 'School': 'School'},
             color='color',
             color_discrete_map=custom_colors  # Apply the custom color mapping
            )
fig.update_layout(xaxis_title='School',
                  yaxis_title=metric,
                  xaxis={'categoryorder':'total descending'})

# Container for the chart
with st.container():
    st.plotly_chart(fig)

# JANUARY VS JULY ASSESSMENTS
st.markdown("---")
st.header("Initial & Midline Assessment Comparisons")
st.info("Clarkson started from a very low base compared to most Masi schools, however all grades made very good progress. The ECDCs started from a very low base and stayed there.")

assessment_choice = st.selectbox('Select an Assessment:', ('January', 'July'))

if assessment_choice == 'January':
    metric = 'Jan - Total Literacy Score'
else:
    metric = 'June - Total Literacy Score'

grade_choice = st.selectbox('Select a Grade:', ('ECD', 'Grade R', 'Grade 1', 'Grade 2', 'Grade 3'))

if grade_choice == 'ECD':
    filtered_df = children[children['Grade'] == 'PreR']
else:
    filtered_df = children[children['Grade'] == grade_choice]

mean_scores = filtered_df.groupby('School')[metric].mean().reset_index()

# Define custom color mapping
custom_colors = {'Bambino': 'feature', 'Clarkson': 'feature', 'Vukani Day Care': 'feature'}

# Apply custom colors
mean_scores['color'] = mean_scores['School'].apply(lambda x: custom_colors.get(x, 'control'))

fig = px.bar(mean_scores,
             x='School',
             y=metric,
             title=f'{metric} by School',
             labels={metric: 'Mean Literacy Score', 'School': 'School'},
             color='color',  # Use the custom color column for coloring
             color_discrete_map=custom_colors  # Apply the custom color mapping
            )
fig.update_layout(xaxis_title='School',
                  yaxis_title=metric,
                  xaxis={'categoryorder':'total descending'})

# Container for the chart
with st.container():
    st.plotly_chart(fig)

# METRIC IMPROVEMENT PER GRADE
st.markdown("---")
st.header("Literacy Skills Gained Per Grade")

grade_choice = st.selectbox('Select a Grade:', ('Grade R', 'Grade 1', 'Grade 2', 'Grade 3'), key='skills')

df = children[children['School'] == "Clarkson"]
filtered_df = df[df['Grade'] == grade_choice]

mean_improvements = filtered_df.agg({
    "June - Letter Sounds Improvement": 'mean',
    "June - Story Comprehension Improvement": 'mean',
    "June - Listen First Sound Improvement": 'mean',
    "June - Listen Words Improvement": 'mean',
    "June - Writing Letters Improvement": 'mean',
    "June - Read Words Improvement": 'mean',
    "June - Write CVCs Improvement": 'mean',
    "June - Write Sentences Improvement": 'mean',
    "June - Write Story Improvement": 'mean',
})

mean_improvements_df = mean_improvements.reset_index()
mean_improvements_df.columns = ['Metric', 'Mean Improvement']
# Define custom color mapping

fig = px.bar(mean_improvements_df,
             x='Metric',
             y='Mean Improvement',
             title='Improvements per Skill',
             labels={'Mean Improvement': 'Mean Improvement Score'},
            )
fig.update_layout(xaxis_title='Metric',
                  yaxis_title='Mean Improvement',
                  xaxis={'categoryorder':'total descending'})

# Container for the chart
with st.container():
    st.plotly_chart(fig)

# TOP PERFORMING CHILDREN
st.markdown("---")
st.header("Top Performing Children")
df = children[(children['School'] == "Clarkson") & (children['2024 On Programme'] == "Yes") ]
top_performers = df[['Full Name', 'Grade', 'Jan - Total Literacy Score', 'June - Total Literacy Score','June - Total Literacy Score Improvement']].sort_values('June - Total Literacy Score Improvement', ascending=False).head(25)
st.dataframe(top_performers, height=800)