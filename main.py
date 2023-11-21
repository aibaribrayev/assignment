import streamlit as st
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Time,
    Numeric,
    Text,
    LargeBinary,
    delete,
    select,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "postgresql://aibar.s.ibrayev:N6JZjPLXh9gM@ep-quiet-rice-66989193.eu-central-1.aws.neon.tech/assignment?sslmode=require"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Database models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    given_name = Column(String(255))
    surname = Column(String(255))
    city = Column(String(255))
    phone_number = Column(String(15), unique=True)
    profile_description = Column(Text)
    password = Column(String(255))


class Caregiver(Base):
    __tablename__ = "caregiver"
    caregiver_user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    photo = Column(LargeBinary)
    gender = Column(String(1))
    caregiving_type = Column(String(255))
    hourly_rate = Column(Numeric(5, 2))


class Member(Base):
    __tablename__ = "member"
    member_user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    house_rules = Column(Text)


class Job(Base):
    __tablename__ = "job"
    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    required_caregiving_type = Column(String(255))
    other_requirements = Column(Text)
    date_posted = Column(Date)


class JobApplication(Base):
    __tablename__ = "job_application"
    job_application_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"))
    job_id = Column(Integer, ForeignKey("job.job_id"))
    date_applied = Column(Date)


class Appointment(Base):
    __tablename__ = "appointment"
    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"))
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Integer)
    status = Column(String(255))


Base.metadata.create_all(engine)


def register_caregiver():
    with st.form("caregiver_form", clear_on_submit=True):
        st.subheader("Caregiver Registration")
        given_name = st.text_input("First Name")
        surname = st.text_input("Last Name")
        caregiving_type = st.selectbox(
            "Type of Caregiving",
            ["Babysitter", "Elderly Care", "Playmate for Children"],
        )
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        city = st.text_input("City")
        hourly_rate = st.number_input("Hourly Rate", min_value=0.0, format="%.2f")
        biography = st.text_area("Biography")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            new_user = User(
                email=email,
                given_name=given_name,
                surname=surname,
                city=city,
                phone_number=phone_number,
                profile_description=biography,
                password=password,
            )

            session.add(new_user)
            session.commit()

            new_caregiver = Caregiver(
                caregiver_user_id=new_user.user_id,
                gender=gender[0],
                caregiving_type=caregiving_type,
                hourly_rate=hourly_rate,
            )

            session.add(new_caregiver)
            session.commit()
            st.success("Registered Successfully!")


def register_family_member():
    with st.form("family_member_form", clear_on_submit=True):
        st.subheader("Family Member Registration")
        given_name = st.text_input("First Name", key="fm_first_name")
        surname = st.text_input("Last Name", key="fm_last_name")
        email = st.text_input("Email", key="fm_email")
        phone_number = st.text_input("Phone Number", key="fm_phone")
        password = st.text_input("Password", type="password", key="fm_password")
        city = st.text_input("City", key="fm_city")
        address = st.text_input("Address", key="fm_address")
        house_rules = st.text_area("House Rules", key="fm_house_rules")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            new_user = User(
                email=email,
                given_name=given_name,
                surname=surname,
                city=city,
                phone_number=phone_number,
                password=password,
            )

            session.add(new_user)
            session.commit()

            new_member = Member(
                member_user_id=new_user.user_id,
                house_rules=house_rules,
            )

            session.add(new_member)
            session.commit()
            st.success("Registered Successfully!")


def login_user():
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            user = session.query(User).filter_by(email=email, password=password).first()
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.user_id
                st.success("Logged in successfully!")
                return True
            else:
                st.error("Invalid email or password")
                return False


def logout_user():
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]
    if "user_id" in st.session_state:
        del st.session_state["user_id"]
    st.experimental_rerun()


def view_jobs():
    st.subheader("Available Jobs")
    jobs = session.query(Job).all()
    if not jobs:
        st.warning("No available jobs at the moment.")
    else:
        for job in jobs:
            st.write(f"Job ID: {job.job_id}")
            st.write(f"Caregiving Type: {job.required_caregiving_type}")
            st.write(f"Other Requirements: {job.other_requirements}")
            st.write(f"Date Posted: {job.date_posted}")
            st.write("---")


def get_user_role(user_id):
    if session.query(Caregiver).filter_by(caregiver_user_id=user_id).first():
        return "caregiver"
    elif session.query(Member).filter_by(member_user_id=user_id).first():
        return "family_member"
    else:
        return "unknown"


def main_page():
    st.title("Welcome to the Caregiver Platform")

    # Check if the user is logged in
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        user_id = st.session_state["user_id"]
        user = session.query(User).get(user_id)

        # Display user profile information
        if user:
            st.subheader("Your Profile")
            st.text(f"Name: {user.given_name} {user.surname}")
            st.text(f"Email: {user.email}")
            st.text(f"City: {user.city}")
            st.text(f"Phone Number: {user.phone_number}")
            st.text(f"Profile Description: {user.profile_description}")

            # Additional information based on role (Caregiver/Member)
            if (
                session.query(Caregiver)
                .filter(Caregiver.caregiver_user_id == user_id)
                .first()
            ):
                caregiver_info = (
                    session.query(Caregiver)
                    .filter(Caregiver.caregiver_user_id == user_id)
                    .first()
                )
                st.subheader("Caregiver Information")
                st.text(f"Caregiving Type: {caregiver_info.caregiving_type}")
                st.text(f"Hourly Rate: {caregiver_info.hourly_rate}")
            elif session.query(Member).filter(Member.member_user_id == user_id).first():
                member_info = (
                    session.query(Member)
                    .filter(Member.member_user_id == user_id)
                    .first()
                )
                st.subheader("Member Information")
                st.text(f"House Rules: {member_info.house_rules}")
        else:
            st.error("User not found.")
    else:
        st.subheader("Please log in to view your profile.")


def post_job_page():
    st.title("Post a Job")
    caregiving_type = st.selectbox(
        "Caregiving Type",
        ["Babysitter", "Elderly Care", "Playmate for Children"],
        key="job_caregiving_type",
    )
    other_requirements = st.text_area(
        "Other Requirements", key="job_other_requirements"
    )
    submit_button = st.button("Post Job")

    if submit_button:
        new_job = Job(
            member_user_id=st.session_state["user_id"],
            required_caregiving_type=caregiving_type,
            other_requirements=other_requirements,
            date_posted=datetime.now().date(),
        )
        try:
            session.add(new_job)
            session.commit()
            st.success("Job Posted Successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            session.rollback()


def apply_for_job():
    st.subheader("Apply for a Job")
    available_jobs = session.query(Job).all()
    if available_jobs:
        job_id = st.selectbox("Select a Job", [job.job_id for job in available_jobs])
        submit_button = st.button("Apply")

        if submit_button:
            job_application = JobApplication(
                caregiver_user_id=st.session_state["user_id"],
                job_id=job_id,
                date_applied=datetime.now().date(),
            )
            session.add(job_application)
            try:
                session.commit()
                st.success("Successfully applied for the job!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                session.rollback()
    else:
        st.warning("No available jobs to apply for.")


# Define a new function to view the job poster's profile
def view_job_poster_profile(session, job_poster_user_id):
    st.title("Job Poster's Profile")

    # Query the database to retrieve the job poster's information
    job_poster = session.query(User).filter_by(user_id=job_poster_user_id).first()

    if job_poster:
        st.subheader("Profile Information")
        st.write(f"Name: {job_poster.given_name} {job_poster.surname}")
        st.write(f"Email: {job_poster.email}")
        st.write(f"City: {job_poster.city}")
        st.write(f"Phone Number: {job_poster.phone_number}")
        st.write(f"Profile Description: {job_poster.profile_description}")

        # Additional information based on role (Caregiver/Member)
        caregiver_info = (
            session.query(Caregiver)
            .filter(Caregiver.caregiver_user_id == job_poster_user_id)
            .first()
        )
        if caregiver_info:
            st.subheader("Caregiver Information")
            st.write(f"Caregiving Type: {caregiver_info.caregiving_type}")
            st.write(f"Hourly Rate: {caregiver_info.hourly_rate}")

        member_info = (
            session.query(Member)
            .filter(Member.member_user_id == job_poster_user_id)
            .first()
        )
        if member_info:
            st.subheader("Member Information")
            st.write(f"House Rules: {member_info.house_rules}")
    else:
        st.error("Job poster not found.")


def arrange_appointment(i):
    st.session_state["arrange_appointment_index"] = i


def view_applications_and_appointments():
    st.subheader("View Job Applications and Create Appointments")
    user_id = st.session_state["user_id"]

    family_member_jobs = session.query(Job).filter(Job.member_user_id == user_id).all()

    if family_member_jobs:
        selected_job_id = st.selectbox(
            "Select a Job to Manage Applications and Appointments",
            [job.job_id for job in family_member_jobs],
        )

        selected_job = next(
            (job for job in family_member_jobs if job.job_id == selected_job_id), None
        )

        if selected_job:
            st.write(f"Job ID: {selected_job.job_id}")
            st.write(f"Caregiving Type: {selected_job.required_caregiving_type}")
            st.write(f"Other Requirements: {selected_job.other_requirements}")
            st.write(f"Date Posted: {selected_job.date_posted}")

            applications = (
                session.query(JobApplication)
                .filter(JobApplication.job_id == selected_job_id)
                .all()
            )

            if applications:
                st.subheader("Job Applications")
                for i, application in enumerate(applications):
                    caregiver_info = (
                        session.query(User.given_name)
                        .join(Caregiver, User.user_id == Caregiver.caregiver_user_id)
                        .filter(
                            Caregiver.caregiver_user_id == application.caregiver_user_id
                        )
                        .first()
                    )

                    st.write(f"Application ID: {application.job_application_id}")
                    if caregiver_info:
                        caregiver_given_name = caregiver_info.given_name
                        st.write(f"Applicant: {caregiver_given_name}")
                    st.write(f"Application Date: {application.date_applied}")

                    arrange_button_key = f"arrange_appointment_{i}"
                    st.button(
                        f"Arrange Appointment with {caregiver_given_name}",
                        key=arrange_button_key,
                        on_click=arrange_appointment,
                        args=(i,),
                    )

                    # Add a button to view the job poster's profile
                    view_profile_key = f"view_profile_{application.job_application_id}_{selected_job.member_user_id}"
                    if st.button("View Job Poster Profile", key=view_profile_key):
                        view_job_poster_profile(session, selected_job.member_user_id)

                    # Check if the arrange appointment button was clicked
                    if st.session_state.get("arrange_appointment_index") == i:
                        # Allow the user to select the appointment date and time
                        appointment_date = st.date_input(
                            "Select Appointment Date",
                            key=f"date_{i}",
                            min_value=datetime.today(),
                        )
                        appointment_time = st.time_input(
                            "Select Appointment Time", key=f"time_{i}"
                        )

                        # Collect additional details for the appointment (work hours, for example)
                        work_hours = st.number_input(
                            "Total Hours for Caregiving Service",
                            key=f"hours_{i}",
                            min_value=1,
                            max_value=24,
                            value=8,
                        )

                        confirm_button_key = f"confirm_{i}"
                        if st.button("Confirm Appointment", key=confirm_button_key):
                            appointment_datetime = datetime.combine(
                                appointment_date, appointment_time
                            )
                            status = "confirmed"

                            new_appointment = Appointment(
                                caregiver_user_id=application.caregiver_user_id,
                                member_user_id=user_id,
                                appointment_date=appointment_datetime.date(),
                                appointment_time=appointment_datetime.time(),
                                work_hours=work_hours,
                                status=status,
                            )

                            session.add(new_appointment)

                            try:
                                session.commit()
                                st.success("Appointment created successfully!")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
                                session.rollback()

            else:
                st.warning("No job applications for this job.")
        else:
            st.warning("Selected job not found.")
    else:
        st.warning("You have not posted any jobs yet.")


def view_appointments_caregiver(session, caregiver_user_id):
    st.title("View Appointments")

    # Query for caregiver's appointments
    caregiver_appointments = (
        session.query(Appointment, User, Caregiver, User)
        .join(User, User.user_id == Appointment.member_user_id)
        .join(Caregiver, Caregiver.caregiver_user_id == Appointment.caregiver_user_id)
        .filter(Appointment.caregiver_user_id == caregiver_user_id)
        .all()
    )

    if caregiver_appointments:
        st.subheader("Your Appointments")
        for appointment, member_user, caregiver, user in caregiver_appointments:
            st.write(f"Appointment ID: {appointment.appointment_id}")
            st.write(f"Member Name: {member_user.given_name} {member_user.surname}")
            st.write(f"Caregiver Name: {user.given_name} {user.surname}")
            st.write(f"Appointment Date: {appointment.appointment_date}")
            st.write(f"Appointment Time: {appointment.appointment_time}")
            st.write(f"Work Hours: {appointment.work_hours}")
            st.write(f"Status: {appointment.status}")

    else:
        st.info("No appointments found for you.")


def main_page():
    st.title("Welcome to the Caregiver Platform")

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        user_id = st.session_state["user_id"]
        user = session.query(User).get(user_id)

        if user:
            st.subheader("Your Profile")
            st.text(f"Name: {user.given_name} {user.surname}")
            st.text(f"Email: {user.email}")
            st.text(f"City: {user.city}")
            st.text(f"Phone Number: {user.phone_number}")
            st.text(f"Profile Description: {user.profile_description}")

            if (
                session.query(Caregiver)
                .filter(Caregiver.caregiver_user_id == user_id)
                .first()
            ):
                caregiver_info = (
                    session.query(Caregiver)
                    .filter(Caregiver.caregiver_user_id == user_id)
                    .first()
                )
                st.subheader("Caregiver Information")
                st.text(f"Caregiving Type: {caregiver_info.caregiving_type}")
                st.text(f"Hourly Rate: {caregiver_info.hourly_rate}")
            elif session.query(Member).filter(Member.member_user_id == user_id).first():
                member_info = (
                    session.query(Member)
                    .filter(Member.member_user_id == user_id)
                    .first()
                )
                st.subheader("Member Information")
                st.text(f"House Rules: {member_info.house_rules}")
        else:
            st.error("User not found.")
    else:
        st.subheader("Please log in to view your profile.")


def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    session = Session()

    if st.session_state["logged_in"]:
        user_role = get_user_role(st.session_state["user_id"])

        main_page()

        if user_role == "family_member":
            selected_page = st.sidebar.radio(
                "Navigation", ["Home", "Post Job", "View Applications and Appointments"]
            )
            if selected_page == "Post Job":
                post_job_page()
            elif selected_page == "View Applications and Appointments":
                view_applications_and_appointments()
        elif user_role == "caregiver":
            selected_page = st.sidebar.radio(
                "Navigation",
                ["Home", "View Jobs", "Apply For Job", "View Appointments"],
            )
            if selected_page == "View Jobs":
                view_jobs()
            if selected_page == "Apply For Job":
                apply_for_job()
            if selected_page == "View Appointments":
                caregiver_user_id = st.session_state["user_id"]
                view_appointments_caregiver(session, caregiver_user_id)
    else:
        menu = st.sidebar.radio(
            "Menu", ["Login", "Register as Caregiver", "Register as Family Member"]
        )
        if menu == "Login":
            if login_user():
                st.write("Welcome to your dashboard!")
        elif menu == "Register as Caregiver":
            register_caregiver()
        elif menu == "Register as Family Member":
            register_family_member()


if __name__ == "__main__":
    main()
