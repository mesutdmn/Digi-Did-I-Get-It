
* [Turkish README](https://github.com/mesutdmn/Digi-Did-I-Get-It/blob/main/README.tr.md)

## Multimodal-LLM Powered Multimedia to Q/A Generation System

In this project we developed a fully automated system which generates questions and answers from various multimedia inputs—including PDF, DOCX, PPTX, EPUB, ENEX (evernote), TXT, MP3, MP4, MPEG4, PNG, JPG, JPEG, URLs, YouTube, Spotify, Wikipedia, and direct text input. Users can interact with the interface to answer questions and receive detailed performance feedback with suggestions for improvement.

🚀 **Live Demo**: [Did I Get It](https://digi-btk.streamlit.app/)
* App may crash due to free streamlit cloud limitations. Please run the app locally for better experience.

### ⚙️ **Workflow**:
1. **Input**: Users upload multimedia files or enter URLs.
2. **Processing**: The system extracts text and audio content from the input.
3. **Question Generation**: Large Language Models (LLMs) generate questions from the content.
4. **Interactive Quiz**: Users answer questions directly within the interface.
5. **Feedback & Recommendations**: Performance reports are generated with insights and suggestions for improvement.
6. **Output**: Users receive a detailed report on their performance and areas for growth.
7. **Repeat**: Users can upload new content and continue the learning process.
8. **Extra**: Questions and Answers can be saved as PDFs after solving the quiz.

![App Workflow](https://github.com/user-attachments/assets/34fcf8c0-fab5-4f58-9c5e-5845febaa43f)

### 📂 **Project Structure**:

```
Digi-Did-I-Get-It/
├── app.py                     # Main Streamlit application file.
├── question_format.py         # Defines the format and structure of questions for the quiz.
├── all_loaders.py             # Handles loading of different file types (e.g., PDF, URL, audio, video).
├── parallel_llm.py            # Manages parallel LLM calls for efficient question generation.
├── utils.py                   # Contains utility functions for shared functionality across files.
├── graph.py                   # Contains structure of Question Generation, Report Generation, and helper LLMs.
├── requirements.txt           # Lists dependencies required for running the project.
├── requirements_with...txt    # Lists dependencies with specific versions for reproducibility.
├── packages.txt               # Lists OS-level packages required for the project.
├── media/                     # Directory for project media files.
│   └── background.jpg         # Background image for the project.
├── styles/                    # Contains styling and fonts for the user interface.
│   ├── style.css              # Custom CSS for styling the Streamlit interface.
│   ├── script.js              # Overwrites some Streamlit functions for additional interactivity.
│   └── arial-unicode-ms.ttf   # Arial Unicode MS for several alphabet support.(Latin, Greek, Cyrillic, Arabic, Chinese, Korean etc.)
├── README.md                  # English project documentation file.
└── README.tr.md               # Turkish project documentation file.

```
### 🎯 **Use Cases**:
- **Education**: Learners can reinforce their learning by answering questions generated from multimedia content.
- **Training & Development**: Professionals can enhance their knowledge retention and comprehension of training materials.
- **Personal Growth**: Individuals can learn new concepts from multimedia content and assess their understanding.
- **Content Creation**: Creators can generate quizzes from their multimedia content for interactive learning experiences.
- **Research & Analysis**: Researchers can extract questions from academic papers, reports, and multimedia sources for analysis.
- **Language Learning**: Language learners can practice reading, listening, and comprehension skills with multimedia content.
- **Entertainment**: Users can engage with multimedia content in a fun and interactive way through quizzes.
- **Skill Development**: Users can test their skills and knowledge in various domains by answering questions from multimedia content.
- **Knowledge Sharing**: Users can create quizzes from multimedia content to share with others for educational purposes.
- **Training Evaluation**: Trainers can assess the effectiveness of training programs by generating questions from multimedia training materials.
- **Interactive Learning**: Users can engage with multimedia content interactively by answering questions generated from the content.


### 🛠️ **Technologies Used**
- **LangChain, LangGraph, LangChain-Core, LangChain-Google-GenAI, LangChain-Community, LangChain-Text-Splitters**: For processing natural language and managing multimodal input data.
- **Pydantic**: To structure data and ensure model consistency.
- **Streamlit**: Builds the user interface, providing an interactive environment for answering questions.
- **PDF & Document Processing**: Libraries such as `pypdf`, `python-pptx`, `docx2txt`, and `unstructured[pdf]` handle various document formats.
- **Video & Audio Processing**: `moviepy`, `youtube-transcript-api`, and `yt_dlp` assist in processing multimedia content.
- **Reporting**: `reportlab` and `markdown2` help generate comprehensive PDF reports.

### 🚀 **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/mesutdmn/Digi-Did-I-Get-It.git
   ```
2. Navigate into the project directory:
   ```bash
   cd Digi-Did-I-Get-It
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables in a `.env` file, including API keys needed for Multimodal Gemini Integration and Spotify access.
    ```bash
   GEMINI_API_KEY=YOUR_API_KEY
   SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
   SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
    ```
5. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
   
### 📌 **How to Use**
1. **Upload Content**: Start the application with Streamlit, and upload the multimedia file, text or enter a URL.
2. **Choice Question's Language**: Select the language for question generation.
3. **Answer Questions**: The system will generate questions from the content.
4. **Interactive Quiz**: Choice how many questions you want to answer and start the quiz.
5. **View Report**: After completing the quiz, receive a detailed report showing your performance, insights on weak areas, and improvement suggestions.


### 🌟 **Team Members**
- [Burhan Yıldız](https://www.linkedin.com/in/burhanyildiz/)
- [Hüseyin Baytar](https://www.linkedin.com/in/huseyinbaytar/)
- [Mesut Duman](https://www.linkedin.com/in/mesut-duman/)

### 📺 **Demo Video**

https://github.com/user-attachments/assets/93a9f3fd-4ff8-4cdf-b4f3-86af8208d7be