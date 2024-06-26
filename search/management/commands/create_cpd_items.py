import shutil
from datetime import datetime

from django.core.management.base import BaseCommand

from search.models import CPDLearningEnvironment, CPDQuestion, CPDScale, CPDTimeToFinish
import sqlite3


class Command(BaseCommand):
    COMPETENCIES_QUESTIONS = [
        "frame the course in the context of the study programme",
        "define intended learning outcomes in every course they teach",
        "choose an appropriate assessment method for their course",
        "engage students and arouse interest for the discipline in the class",
        "teach holistically by integrating social and art aspects in teaching and learning complex chemical concepts",
        "cope with heterogeneous pre-knowledge of students",
        "being able to bring out and correct misconceptions",
        "develop critical thinking by students",
        "give prompt feedback and support students during learning",
        "support students in socializing (specifically e.g. during a pandemic)",
        "stimulate discussion",
        "design laboratory courses",
        "teach about lab safety using digital tools/platform (where appropriate)",
        "teach large groups of students",
        "teach small groups of students (group's dynamics)",
        "design interactive lectures",
        "design online exams",
        "design problem solving sessions",
        "design active learning classes / sessions using digital technology",
        "use digital tools in lab courses",
        "use design thinking methods",
        "use research based teaching methods",
        "use project based teaching methods",
        "use blended learning approach",
        "use interactive online boards for teaching and learning",
        "use voting in lectures to activate thinking and understanding of (e.g. chemistry) concepts",
        "organize peer-assessment / peer-feedback in their courses",
        "organize (online) collaborative learning",
        "use advanced tools, based on artificial intelligence, in supporting students in their learning process",
        "make/produce short MOOCs",
    ]

    ATTITUDES_QUESTIONS = [
        "be reflective teachers and reflect about their courses / lectures.",
        "have high expectations for the students and themselves.",
        "inspire a positive attitude in their class.",
        "make students feel special, included, safe and secure.",
        "be interested in their students' progress.",
        "use students evaluations and the feedback of students to improve courses.",
        "read literature about teaching and learning in higher education.",
        "discuss teaching with their colleagues.",
        "observe (some) lectures / teaching sessions of colleagues and give feedback.",
        "record (some) own lectures / teaching sessions on the video to reflect on.",
        "organize / attend meetings of their own teaching team to discuss / reflect on the teaching methods and on the effect of those on students' learning.",
        "share experience and knowledge gained through continuous professional development (CPD) with lecturers from other institutions.",
        "analyse the effect of teaching and introduce changes in an evidence based way.",
        "set their own goals for professional development.",
        "attend training for lecturers at the university.",
        "apply for specific professional development programmes to obtain certificate(s) in teaching.",
        "participate in conferences about teaching in higher education.",
    ]

    ACTIVITIES_QUESTIONS = [
        "reading books / journal articles on teaching and learning in HE.",
        "attending presentations about teaching approaches.",
        "attending webinars about teaching and learning.",
        "attending hands-on workshops on specific continuous professional development (CPD) topics.",
        "following online courses / MOOC about teaching and learning.",
        "attending conferences on teaching and learning in HE.",
        "attending a summer school on teaching and learning.",
        "attending a professional development programme to get a teaching certificate in higher education (if it doesn't exist in your country, please indicate in General importance what is your personal opinion about it and choose in Personal practice not applicable).",
        "attending workshops that are organized specifically for STEM lecturers.",
        "attending workshops that are organized generally for lecturers from different disciplines.",
        "collaborating with a peer-lecturer on a redesign of a course.",
        "getting peer-feedback on own teaching practice from a colleague.",
        "collaborating on a teaching innovation project.",
        "getting personal coaching / support by a pedagogical expert.",
        "getting mentoring from an experienced colleague.",
        "getting just-in-time support on a specific teaching and learning issue.",
        "giving mentoring to a junior lecturer.",
        "giving workshops to other lecturers.",
        "participating in a teaching and learning network or a special interest group on teaching and learning in HE.",
    ]

    COMPETENCES_SCALES_QUESTIONS = [
        ("1", "Constructive alignment", "sound course design", []),
        ("1a", "Constructive alignment", "sound course design", [1, 2, 3, 6]),
        (
            "2",
            "Interactive teaching",
            "interactive teaching",
            [],
        ),
        ("2a", "Competence teaching", "teaching in higher education", [9, 10, 14, 15]),
        (
            "2b",
            "Competence design interactive teaching",
            "designing interactive teaching",
            [16, 19],
        ),
        (
            "3",
            "Learning facilitation",
            "learning facilitation",
            [],
        ),
        (
            "3a",
            "Problem solving (design and teaching)",
            "facilitating problem solving",
            [18, 21, 22, 23],
        ),
        (
            "3b",
            "Engagement and motivation, facilitation discipline specific learning",
            "how to engage and motivate students and how to facilitate discipline specific thinking",
            [4, 12, 13],
        ),
        (
            "3c",
            "Deep learning",
            "how to facilitate student’s deep learning and development of higher cognitive skills",
            [5, 7, 8, 11],
        ),
        (
            "3d",
            "Organize peer-feedback, collaborative learning",
            "organizing peer-feedback and collaborative learning ",
            [27, 28],
        ),
        (
            "4",
            "Technology in facilitative teaching:",
            "use of technology in facilitative teaching",
            [],
        ),
        (
            "4a",
            "Use of digital tools for a pedagogical goal",
            "how to use specific digital tools in teaching for a pedagogical goal",
            [17, 25, 26, 29, 30],
        ),
        (
            "4b",
            "Blended learning",
            "how to use blended learning",
            [20, 24],
        ),
    ]

    ATTITUDES_SCALES_QUESTIONS = [
        (
            "1",
            "Motivation and self-regulation for CPD",
            "how to stay motivated and self-regulate their continuous professional development",
            [],
        ),
        (
            "1a",
            "Motivation and self-regulation for CPD",
            "how to stay motivated and self-regulate their continuous professional development",
            [2, 14, 15, 16],
        ),
        (
            "2",
            "Pastoral interest",
            "supporting student development and enabling students’ well-being in a learning process and inclusivity",
            [],
        ),
        (
            "2a",
            "Pastoral interest",
            "supporting student development and enabling students’ well-being in a learning process and inclusivity",
            [3, 4, 5],
        ),
        ("3", "Reflection", "reflecting on own teaching practice", []),
        ("3a", "Reflection", "reflecting on own teaching practice", [1, 10, 11]),
        (
            "4",
            "Evidence informed approach",
            "practicing teaching and learning in an evidence informed way ",
            [],
        ),
        (
            "4a",
            "Evidence informed approach",
            "practicing teaching and learning in an evidence informed way ",
            [6, 7, 13],
        ),
        ("5", "Knowledge sharing", "knowledge sharing", []),
        ("5a", "Knowledge sharing", "knowledge sharing", [8, 9, 12, 17]),
    ]

    ACTIVITIES_SCALES_QUESTIONS = [
        (
            "1",
            "Imparting information (trainer-centered)",
            "a trainer centered way",
            [],
        ),
        (
            "1a",
            "Imparting information (trainer-centered)",
            "a trainer centered way",
            [1, 2, 3],
        ),
        (
            "2",
            "Learning facilitation (person-centered)",
            "a learner centered way",
            [],
        ),
        (
            "2a",
            "Learning facilitation (person-centered)",
            "a learner centered way",
            [4, 5, 7, 8, 9, 10],
        ),
        ("3", "Collaboration", "collaboratively", []),
        ("3a", "Collaboration", "collaboratively", [11, 13]),
        (
            "4",
            "Mentor-mentee support",
            "according to mentor-mentee support principle",
            [],
        ),
        (
            "4a",
            "Mentor-mentee support",
            "according to mentor-mentee support principle",
            [12, 15, 17],
        ),
        (
            "5",
            "(Personal/individual) expert support",
            "by using personal/individual expert support",
            [],
        ),
        (
            "5a",
            "(Personal/individual) expert support",
            "by using personal/individual expert support",
            [14, 16],
        ),
        ("6", "Knowledge sharing", "by knowledge sharing", []),
        ("6a", "Knowledge sharing", "by knowledge sharing", [6, 18, 19]),
    ]

    TIME_TO_FINISH_ENTRIES = [
        ("Several hours", "several hours"),
        ("Several days", "several days"),
        ("Several weeks", "several weeks"),
        ("Several months", "several months"),
    ]

    LEARNING_ENVIRONMENT_ENTRIES = [
        ("μMOOCs", "are using a very short open online course, a micro MOOC (μMOOC)"),
        (
            "Workplace",
            "professionalize in a close connection to their own teaching practice (at their workplace)",
        ),
        (
            "Face-to-face",
            "meet in person on location with the training staff and with other participants",
        ),
    ]

    def add_arguments(self, parser):
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        # create backup of existing database
        path_to_db = options["path_to_db"]
        shutil.copyfile(
            path_to_db,
            path_to_db + "_backup_pre_create_cpd_items_" + datetime.now().strftime("%m.%d.%Y_%H.%M.%S"),
        )

        print("Reseting tables...")
        # We need to delete the old entries in order to regenerate the questions. Aside from deleting we also want to reset the pk counter, which for some questions start at odd values in order to preserve the links between case and questions etc, presumably due to incorrect edits in the past.
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM search_cpdscale;")
        cursor.execute("UPDATE sqlite_sequence SET seq = 54 WHERE name = 'search_cpdscale';")
        cursor.execute("DELETE FROM search_cpdactivity;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'search_cpdactivity';")
        cursor.execute("DELETE FROM search_cpdlearningenvironment;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'search_cpdlearningenvironment';")
        cursor.execute("DELETE FROM search_cpdquestion;")
        cursor.execute("UPDATE sqlite_sequence SET seq = 140 WHERE name = 'search_cpdquestion';")
        cursor.execute("DELETE FROM search_cpdtimetofinish;")
        cursor.execute("UPDATE sqlite_sequence SET seq = 8 WHERE name = 'search_cpdtimetofinish';")
        connection.commit()

        print("Creating competences")
        self.insert_scale_data(
            CPDScale.ST_COMPETENCES,
            self.COMPETENCES_SCALES_QUESTIONS,
            self.COMPETENCIES_QUESTIONS,
        )
        print("Creating attitudes")
        self.insert_scale_data(
            CPDScale.ST_ATTITUDES,
            self.ATTITUDES_SCALES_QUESTIONS,
            self.ATTITUDES_QUESTIONS,
        )
        print("Creating activities")
        self.insert_scale_data(
            CPDScale.ST_ACTIVITIES,
            self.ACTIVITIES_SCALES_QUESTIONS,
            self.ACTIVITIES_QUESTIONS,
        )

        print("Saving time to finish")
        for title, inline_title in self.TIME_TO_FINISH_ENTRIES:
            ttf = CPDTimeToFinish(title=title, inline_title=inline_title)
            ttf.save()

        print("Saving learning environments")
        for title, inline_title in self.LEARNING_ENVIRONMENT_ENTRIES:
            le = CPDLearningEnvironment(title=title, inline_title=inline_title)
            le.save()

    def insert_scale_data(self, scale_type, scale_data, questions):
        # create parent scales
        for scale, title, inline_title, scale_questions in scale_data:
            # parent scales don't have questions
            if scale_questions:
                continue

            s = CPDScale(
                title=title,
                inline_title=inline_title,
                scale=scale,
                scale_type=scale_type,
            )
            s.save()

        # create other scales
        for scale, title, inline_title, scale_questions in scale_data:
            # parent scales don't have questions
            # and we already created the parent scales
            if not scale_questions:
                continue

            # scale is always "Nn" or "N" where N is the parent scale
            # and n is the child scale
            parent_scale = None if len(scale) == 1 else scale[0]
            scale = scale[0] if not parent_scale else scale[1]

            s = CPDScale(
                title=title,
                inline_title=inline_title,
                scale=scale,
                scale_parent=CPDScale.objects.get(scale_type=scale_type, scale=parent_scale) if parent_scale else None,
                scale_type=scale_type,
            )
            s.save()

            for scale_question in scale_questions:
                # scale_question is an index starting at 1
                q = CPDQuestion(scale=s, question=questions[scale_question - 1], question_nr=scale_question)
                q.save()
