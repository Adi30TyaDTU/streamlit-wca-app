import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

st.sidebar.title("Message Metrics : A Chat Analyser")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    st.dataframe(df)
    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages,words,num_media_messages,num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Titles and layout for each section
        st.title("Chat Analysis Dashboard")

        # Monthly Timeline
        st.header("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(16, 10))  # Increase figsize
        ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
        ax.set_xlabel('Month-Year', fontsize=14)
        ax.set_ylabel('Number of Messages', fontsize=14)
        ax.set_title('Monthly Message Timeline', fontsize=18, fontweight='bold')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Daily Timeline
        st.header("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(16, 10))  # Increase figsize
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', marker='o')
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Number of Messages', fontsize=14)
        ax.set_title('Daily Message Timeline', fontsize=18, fontweight='bold')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Activity Map
        st.header("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(16, 10))  # Increase figsize
            ax.bar(busy_day.index, busy_day.values, color='purple')
            ax.set_xlabel('Day of the Week', fontsize=14)
            ax.set_ylabel('Number of Messages', fontsize=14)
            ax.set_title('Most Busy Day', fontsize=18, fontweight='bold')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.subheader("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(16, 10))  # Increase figsize
            ax.bar(busy_month.index, busy_month.values, color='orange')
            ax.set_xlabel('Month', fontsize=14)
            ax.set_ylabel('Number of Messages', fontsize=14)
            ax.set_title('Most Busy Month', fontsize=18, fontweight='bold')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Weekly Activity Map
        st.header("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(16, 10))  # Increase figsize
        sns.heatmap(user_heatmap, cmap="YlGnBu", ax=ax, linewidths=0.5, linecolor='white')
        ax.set_title('Weekly Activity Heatmap', fontsize=18, fontweight='bold')
        ax.set_xlabel('Hour of the Day', fontsize=14)
        ax.set_ylabel('Day of the Week', fontsize=14)
        plt.xticks(rotation=45)
        st.pyplot(fig)


        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Get most common words data
        sns.set(style="whitegrid")
        most_common_df = helper.most_common_words(selected_user, df)

        # Rename columns for clarity
        most_common_df.columns = ['Words', 'Frequency']

        # Display data as a dataframe in Streamlit with customized column names
        st.dataframe(
            most_common_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'left')]}]
            ).background_gradient(cmap='Blues')
        )
        # Create a bar plot for the most common words
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotting the bar chart with Seaborn for a better aesthetic
        sns.barplot(x=most_common_df['Frequency'], y=most_common_df['Words'], palette='viridis', ax=ax)

        # Adding titles and labels
        ax.set_title('Most Common Words', fontsize=16, fontweight='bold')
        ax.set_xlabel('Frequency', fontsize=14)
        ax.set_ylabel('Words', fontsize=14)

        # Setting font properties to handle emojis
        for label in ax.get_yticklabels():
            label.set_fontproperties('DejaVu Sans')

        # Adjust layout for better spacing
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)

        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")

            # Setting font properties for the pie chart to display emojis
            emoji_font = FontProperties(family='DejaVu Sans')
            for text in ax.texts:
                text.set_fontproperties(emoji_font)

            st.pyplot(fig)


