"""Example jobs for the 'Load an example job' dropdown.

To add a job, add one line under a category:
    "Job title": (years_of_experience, "skill, skill, skill", "Qualification text"),
Use 0 years for freshers. Use skill words that exist in skills_db.py (or add them there).
"""

JOBS = {
    "Hospitality": {
        "Hotel Management Trainee": (0, "front office, housekeeping, food and beverage service, guest service, english communication, teamwork, attention to detail, adaptability", "Bachelor's degree in hotel management"),
        "Front Office Executive": (2, "front office, reservations, check-in/check-out, guest service, Opera PMS, upselling, complaint handling, english communication, teamwork", "Diploma or bachelor's degree in hotel management"),
        "Reservations Executive": (1, "reservations, hotel software, english communication, upselling, customer service, ms office, multitasking", "Bachelor's degree"),
        "Guest Relations Executive": (2, "guest relations, concierge, complaint handling, english communication, problem solving, grooming, multitasking", "Bachelor's degree in hotel management"),
        "Housekeeping Supervisor": (3, "housekeeping, laundry, inventory management, teamwork, leadership, time management, attention to detail, safety and security", "Diploma in hotel management"),
        "Food and Beverage Service Associate": (1, "food and beverage, food service, guest service, upselling, menu knowledge, teamwork, grooming, english communication", "Diploma in hotel management"),
        "Restaurant Manager": (5, "food and beverage, leadership, guest service, complaint handling, inventory management, cash handling, time management, food safety", "Bachelor's degree in hotel management"),
        "Commis Chef / Kitchen Trainee": (0, "cooking, kitchen operations, food safety, bakery, teamwork, time management, grooming", "Diploma in culinary arts"),
        "Banquet and Event Executive": (2, "banquet, event management, food and beverage, guest service, teamwork, communication, time management, multitasking", "Bachelor's degree"),
        "Bartender / Barista": (1, "bartending, food and beverage, guest service, cash handling, upselling, teamwork, grooming", "Diploma in hotel management"),
        "Hotel Revenue Analyst": (3, "revenue management, excel, data analysis, reservations, hotel software, communication, attention to detail", "Bachelor's degree in hotel management"),
        "Hotel Management Intern": (0, "front office, reservations, guest service, check-in/check-out, housekeeping, food and beverage service, banquet, event management, english communication, teamwork, time management, multitasking, ms office, grooming, complaint handling, food safety", "Pursuing a degree in hotel management"),
    },
    "Software and IT": {
        "Software Engineer Trainee (Fresher)": (0, "Python, Java, SQL, Git, problem solving, communication, teamwork", "Bachelor's degree in computer science"),
        "Python Developer": (3, "Python, Django, SQL, Docker, Git, REST API, AWS, communication, teamwork", "Bachelor's degree in computer science"),
        "Java Developer": (3, "Java, Spring Boot, SQL, REST API, Git, Docker, problem solving, teamwork", "Bachelor's degree in computer science"),
        "Frontend Developer": (2, "JavaScript, React, HTML, CSS, TypeScript, Git, REST API, teamwork", "Bachelor's degree in computer science"),
        "Full Stack Developer": (3, "JavaScript, React, Node.js, MongoDB, SQL, REST API, Git, Docker, problem solving", "Bachelor's degree in computer science"),
        "Mobile App Developer": (2, "Kotlin, Java, Firebase, REST API, Git, problem solving, teamwork", "Bachelor's degree in computer science"),
        "DevOps Engineer": (3, "AWS, Docker, Kubernetes, Linux, CI/CD, Git, Python, problem solving", "Bachelor's degree in computer science"),
        "Cloud Engineer": (3, "AWS, Azure, GCP, Linux, Docker, Kubernetes, CI/CD, communication", "Bachelor's degree in computer science"),
        "Software Tester (QA)": (2, "software testing, SQL, Git, REST API, attention to detail, communication, problem solving", "Bachelor's degree in computer science"),
        "UI/UX Designer": (2, "ui/ux design, graphic design, creativity, communication, teamwork, presentation", "Bachelor's degree in design"),
    },
    "Data and AI": {
        "Data Analyst": (2, "SQL, Python, Excel, Pandas, data visualization, statistics, communication", "Bachelor's degree"),
        "Data Scientist": (3, "Python, machine learning, statistics, SQL, Pandas, scikit-learn, data visualization, communication", "Bachelor's degree in statistics or computer science"),
        "Machine Learning Engineer": (2, "Python, machine learning, deep learning, TensorFlow, PyTorch, scikit-learn, Pandas, NumPy, SQL, Git", "Bachelor's degree in computer science"),
        "NLP Engineer": (2, "Python, NLP, deep learning, PyTorch, machine learning, Git, problem solving", "Bachelor's degree in computer science"),
        "Business Analyst": (3, "data analysis, SQL, Excel, presentation, communication, project management, problem solving", "Bachelor's degree"),
    },
    "Business and Management": {
        "Digital Marketing Executive": (2, "digital marketing, SEO, content writing, graphic design, Excel, communication, creativity", "Bachelor's degree"),
        "Social Media Manager": (2, "marketing, content writing, graphic design, video editing, communication, creativity", "Bachelor's degree"),
        "Sales Executive": (1, "sales, negotiation, communication, presentation, customer support, ms office", "Bachelor's degree"),
        "HR Executive": (2, "human resources, recruitment, communication, ms office, negotiation, time management", "Bachelor's degree"),
        "Accountant": (2, "accounting, GST, Excel, Tally, attention to detail, ms office", "Bachelor's degree in commerce"),
        "Project Manager": (5, "project management, agile, leadership, communication, negotiation, time management, presentation", "Bachelor's degree"),
        "Operations Executive": (2, "supply chain, inventory management, Excel, communication, time management, problem solving", "Bachelor's degree"),
        "Office Administrator": (1, "ms office, communication, time management, multitasking, data entry, problem solving", "Bachelor's degree"),
    },
    "Customer Service and Support": {
        "Customer Support Executive": (1, "customer support, communication, problem solving, english communication, complaint handling, ms office", "Bachelor's degree"),
        "Call Center Associate": (0, "customer care, english communication, communication, complaint handling, typing speed, teamwork", "Higher secondary or any degree"),
        "Data Entry Operator": (0, "data entry, ms office, Excel, attention to detail, time management", "Higher secondary or any degree"),
    },
    "Creative and Media": {
        "Content Writer": (1, "content writing, SEO, research, english communication, creativity, time management", "Bachelor's degree"),
        "Graphic Designer": (2, "graphic design, video editing, creativity, communication, time management", "Bachelor's degree or diploma in design"),
    },
    "Healthcare and Education": {
        "Staff Nurse": (1, "patient care, first aid, teamwork, communication, attention to detail, problem solving, adaptability", "Diploma in nursing or bachelor's degree in nursing"),
        "School Teacher": (2, "teaching, classroom management, communication, leadership, creativity, time management, ms office", "Bachelor's degree"),
        "Online Tutor": (1, "tutoring, communication, english communication, creativity, time management", "Bachelor's degree"),
    },
}


def build_description(title, years, skills, education):
    lines = [title]
    lines.append(f"Experience: {years}+ years." if years else "Freshers are welcome.")
    lines.append(f"Required skills: {skills}.")
    if education:
        lines.append(f"Qualification: {education}.")
    return "\n".join(lines)


# label shown in the dropdown -> full job description text
JOB_PRESETS = {"- choose an example job -": ""}
for category, jobs in JOBS.items():
    for title, (years, skills, education) in jobs.items():
        JOB_PRESETS[f"{category} · {title}"] = build_description(title, years, skills, education)
