import streamlit as st  # Web UI
import pandas as pd  # Data handling
import matplotlib.pyplot as plt  # Plotting
import seaborn as sns  # Enhanced visuals
import re  # Text matching

# Category keywords for automated categorization
CATEGORY_KEYWORDS = {
    'Groceries': ['supermarket', 'grocery', 'market', 'food'],
    'Utilities': ['electricity', 'water', 'gas', 'utility', 'internet', 'phone'],
    'Subscriptions': ['netflix', 'spotify', 'subscription', 'hulu', 'amazon prime'],
    'Restaurants': ['restaurant', 'cafe', 'bar', 'diner', 'food delivery'],
    'Transport': ['uber', 'lyft', 'bus', 'metro', 'train', 'taxi', 'fuel', 'gas station'],
    'Entertainment': ['cinema', 'movie', 'concert', 'theater', 'ticket'],
    'Healthcare': ['pharmacy', 'doctor', 'hospital', 'clinic', 'dental'],
    'Others': []
}

def categorize_transaction(description):  # Categorize by description keywords
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc):  # Word boundary match
                return category
    return 'Others'  # Default category

def load_and_process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)  # Read uploaded CSV
    df = df[['Date', 'Description', 'Amount']]  # Select relevant columns
    df['Category'] = df['Description'].apply(categorize_transaction)  # Auto categorize
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Parse dates
    df.dropna(subset=['Date', 'Amount'], inplace=True)  # Remove invalid rows
    return df

def display_summaries(df):
    by_category = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    by_vendor = df.groupby('Description')['Amount'].sum().sort_values(ascending=False).head(10)
    st.subheader('Spending by Category')
    st.table(by_category)
    st.subheader('Top 10 Vendors by Spending')
    st.table(by_vendor)
    return by_category, by_vendor

def plot_summary(by_category, by_vendor):
    fig, axes = plt.subplots(1, 2, figsize=(12,5))
    sns.barplot(x=by_category.values, y=by_category.index, palette='viridis', ax=axes[0])
    axes[0].set_title('Spending by Category')
    axes[0].set_xlabel('Total Amount')
    axes[0].set_ylabel('Category')

    sns.barplot(x=by_vendor.values, y=by_vendor.index, palette='magma', ax=axes[1])
    axes[1].set_title('Top 10 Vendors')
    axes[1].set_xlabel('Total Amount')
    axes[1].set_ylabel('Vendor')

    st.pyplot(fig)

def monthly_trends(df):
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_cat = df.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10,6))
    monthly_cat.plot(ax=ax)
    ax.set_title('Monthly Spending Trends by Category')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.legend(title='Category', bbox_to_anchor=(1.05,1), loc='upper left')
    st.pyplot(fig)

def overspending_alert(df):
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_sum = df.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)
    pct_change = monthly_sum.pct_change().fillna(0)
    alerts = pct_change.applymap(lambda x: x > 0.2)

    messages = []
    for month in alerts.index[1:]:
        over_cats = alerts.loc[month]
        triggered = over_cats[over_cats].index.tolist()
        if triggered:
            messages.append(f"In {month}: spending increased >20% in {', '.join(triggered)}")
    if messages:
        st.warning("Overspending Alerts:\n" + "\n".join(messages))
    else:
        st.info("No overspending detected.")

def main():
    st.title("Automated Monthly Spending Tracker")
    uploaded_file = st.file_uploader("Upload your bank CSV file", type=['csv'])
    if uploaded_file:
        df = load_and_process_csv(uploaded_file)
        by_category, by_vendor = display_summaries(df)
        plot_summary(by_category, by_vendor)
        monthly_trends(df)
        overspending_alert(df)

if __name__ == "__main__":
    main()