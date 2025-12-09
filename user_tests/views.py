from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse  # <-- JsonResponse imported
from django.utils import timezone  # <-- timezone imported
from datetime import timedelta  # <-- timedelta imported

# IMPORTS
from app.models import QuestionPaper, Question
from .models import TestRegistration, UserResponse
from .forms import TestRegistrationForm
from django.urls import reverse  # Required for redirecting using named URLs

# --- HELPER FUNCTION FOR FLOW CONTROL ---


def get_session_key(link_id):
    """Generates the unique session key for this test link."""
    return f"test_status_{link_id}"


def check_flow_and_redirect(request, link_id, current_stage_name):
    """
    Checks the user's progress status using the session and registration completion status.
    Returns a HttpResponseRedirect object if a redirect is needed, otherwise returns None.

    Stages:
    1. user_register_link
    2. user_instructions
    3. user_test
    4. user_already_submitted (final state)
    """
    session_key = get_session_key(link_id)
    session_status = request.session.get(session_key, "not_started")

    # Define the strict flow map: where should the user be coming from?
    # Key: Current view name, Value: Required session status to be here
    FLOW_SEQUENCE = [
        "user_register_link",  # not_started
        "user_instructions",  # registered
        "user_test",  # instructed (after POST on instructions)
        "user_already_submitted",  # submitted (final state, checked via DB)
    ]

    current_index = FLOW_SEQUENCE.index(current_stage_name)

    # 1. High Priority Check: Already Submitted (via DB)
    registration_id = request.session.get("current_registration_id")
    if registration_id:
        try:
            reg = TestRegistration.objects.get(pk=registration_id, is_completed=True)
            # If submitted, always go to the final page, unless we are already there.
            if current_stage_name != "user_already_submitted":
                return redirect("test:user_already_submitted")
        except TestRegistration.DoesNotExist:
            pass

    # 2. Flow Enforcement Check (for backward/forward jumps)
    if current_stage_name == "user_register_link":
        # If they successfully registered, push them forward.
        if session_status == "registered":
            return redirect("test:user_instructions", link_id=link_id)
        # If they somehow got to 'instructed' or 'in_progress', send them to test.
        if session_status in ["instructed", "in_progress"]:
            return redirect("test:user_test", link_id=link_id)

    elif current_stage_name == "user_instructions":
        # Must be 'registered' to access instructions.
        if session_status == "not_started":
            return redirect("test:user_register_link", link_id=link_id)
        # If they already accepted instructions, push them to the test.
        if session_status in ["instructed", "in_progress"]:
            return redirect("test:user_test", link_id=link_id)

    elif current_stage_name == "user_test":
        # Must be 'instructed' to access the test.
        if session_status == "not_started":
            return redirect("test:user_register_link", link_id=link_id)
        if session_status == "registered":
            return redirect("test:user_instructions", link_id=link_id)

    # For 'user_already_submitted', we rely on the DB check above.

    return None  # No redirect needed, proceed to view logic


# --- BACKEND TIMER API VIEW ---


def get_time_remaining_api(request, link_id):
    """
    Calculates and returns the time remaining for the currently active test registration.
    This is the backend source of truth for the timer.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    registration_id = request.session.get("current_registration_id")
    if not registration_id:
        # अगर session में registration ID नहीं है, मतलब test flow शुरू नहीं हुआ है
        return JsonResponse({"error": "Registration not found"}, status=403)

    try:
        paper_id = int(link_id)
        paper = get_object_or_404(QuestionPaper, pk=paper_id)

        # Registration ऑब्जेक्ट प्राप्त करें जो in-progress है (is_completed=False)
        registration = get_object_or_404(
            TestRegistration,
            pk=registration_id,
            question_paper=paper,
            is_completed=False,
        )
    except Exception:
        # अगर registration already complete है या कोई और error है
        return JsonResponse({"remaining_seconds": 0, "time_up": True})

    # परीक्षा की अवधि मिनटों में
    duration_minutes = paper.duration

    # समाप्ति का अनुमानित समय (start_time + duration)
    expected_end_time = registration.start_time + timedelta(minutes=duration_minutes)

    # शेष समय की गणना
    time_remaining = expected_end_time - timezone.now()

    remaining_seconds = int(time_remaining.total_seconds())

    # --- Time Up/Auto-Submission Check ---
    if remaining_seconds <= 0:

        # DB में mark करें और session clean up करें (Auto-Submit Logic)
        with transaction.atomic():
            registration.is_completed = True
            registration.save()

            if "current_registration_id" in request.session:
                del request.session["current_registration_id"]

            # Set final session status
            request.session[get_session_key(link_id)] = "submitted"
            request.session.modified = True

        return JsonResponse({"remaining_seconds": 0, "time_up": True})

    return JsonResponse({"remaining_seconds": remaining_seconds, "time_up": False})


# --- VIEWS START HERE ---


def user_register_view(request, link_id):
    """Handles test taker registration."""

    # ... (rest of user_register_view remains unchanged) ...

    # --- FLOW CHECK ---
    redirect_response = check_flow_and_redirect(request, link_id, "user_register_link")
    if redirect_response:
        return redirect_response
    # --- END FLOW CHECK ---

    try:
        paper_id = int(link_id)
        # Check that the paper exists AND is public
        paper = get_object_or_404(QuestionPaper, pk=paper_id, is_public_active=True)
    except (ValueError, QuestionPaper.DoesNotExist):
        messages.error(request, "The test link is invalid or deactivated.")
        return redirect("home")

    # Previous logic to check existing session registration ID and redirect to instructions.
    registration_id = request.session.get("current_registration_id")
    if registration_id:
        try:
            # Check if registration exists and is NOT completed
            reg = TestRegistration.objects.get(
                pk=registration_id, question_paper=paper, is_completed=False
            )
            return redirect("test:user_instructions", link_id=link_id)
        except TestRegistration.DoesNotExist:
            pass

    if request.method == "POST":
        form = TestRegistrationForm(request.POST)
        if form.is_valid():
            try:
                registration = form.save(commit=False)
                registration.question_paper = paper
                registration.save()

                # Set Session for BOTH registration ID and flow status
                request.session["current_registration_id"] = registration.id
                request.session[get_session_key(link_id)] = "registered"
                request.session.modified = True

                messages.success(
                    request, "Registration successful. Please read instructions."
                )

                return redirect("test:user_instructions", link_id=link_id)

            except IntegrityError:
                # Already registered with this email for this paper
                messages.error(
                    request,
                    "You have already registered for this test with this email address.",
                )
                return redirect("test:user_register_link", link_id=link_id)

    else:
        form = TestRegistrationForm()

    context = {
        "form": form,
        "link_id": link_id,
        "paper_title": paper.title,
    }
    response = render(request, "user_test/register.html", context)
    # ************************************************
    # * NEW: AGGRESSIVE CACHING HEADERS ADDED HERE *
    # ************************************************
    response["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


def user_instruction_view(request, link_id):
    """Shows test details and instructions before starting."""

    # ... (rest of user_instruction_view remains unchanged) ...

    # --- FLOW CHECK ---
    redirect_response = check_flow_and_redirect(request, link_id, "user_instructions")
    if redirect_response:
        return redirect_response
    # --- END FLOW CHECK ---

    try:
        paper_id = int(link_id)
        paper = get_object_or_404(QuestionPaper, pk=paper_id, is_public_active=True)
    except (ValueError, QuestionPaper.DoesNotExist):
        return redirect("home")

    registration_id = request.session.get("current_registration_id")
    if not registration_id:
        return redirect("test:user_register_link", link_id=link_id)

    try:
        reg = TestRegistration.objects.get(
            pk=registration_id, question_paper=paper, is_completed=False
        )
    except TestRegistration.DoesNotExist:
        return redirect("test:user_already_submitted")

    # POST: User accepts instructions and starts test
    if request.method == "POST":
        # Set flow status to 'instructed' and redirect to test
        request.session[get_session_key(link_id)] = "instructed"
        request.session.modified = True
        return redirect("test:user_test", link_id=link_id)

    # All checks passed
    return render(
        request, "user_test/instruction.html", {"link_id": link_id, "paper": paper}
    )


def user_test_view(request, link_id):
    """
    Handles the actual test display (GET) and submission (POST).
    """
    # --- FLOW CHECK ---
    redirect_response = check_flow_and_redirect(request, link_id, "user_test")
    if redirect_response:
        return redirect_response
    # --- END FLOW CHECK ---

    # --- GET ACCESS CHECK (Existing logic retained) ---
    try:
        paper_id = int(link_id)
        paper = get_object_or_404(QuestionPaper, pk=paper_id, is_public_active=True)
        registration_id = request.session.get("current_registration_id")

        # We MUST have a registration ID and valid paper
        if not registration_id:
            return redirect("test:user_register_link", link_id=link_id)

        # 1. Registration object fetch karein
        registration = get_object_or_404(
            TestRegistration, pk=registration_id, question_paper=paper
        )

    except Exception:
        return redirect("test:user_register_link", link_id=link_id)

    # ----------------------------------------------------------------------
    # CRITICAL BACK PREVENTION CHECK (DB check - is_completed)
    # ----------------------------------------------------------------------
    if registration.is_completed:
        return redirect("test:user_already_submitted")
    # ----------------------------------------------------------------------

    # We set status to 'in_progress' to clearly indicate the user has started the test.
    request.session[get_session_key(link_id)] = "in_progress"
    request.session.modified = True

    # --- POST SUBMISSION LOGIC ---
    if request.method == "POST":

        with transaction.atomic():

            # 1. User Responses ko save karein (Existing logic retained)
            for key, value in request.POST.items():
                if key.startswith("question_"):
                    question_id = key.split("_")[1]
                    user_answer = value.strip()

                    try:
                        question = Question.objects.get(pk=question_id)

                        # UserResponse object create karein
                        UserResponse.objects.create(
                            registration=registration,
                            question=question,
                            user_answer=user_answer,
                        )
                    except Question.DoesNotExist:
                        continue

            # 2. Test Registration ko COMPLETE mark karein (Existing logic retained)
            registration.is_completed = True
            registration.save()

            # 3. Session clean up (important for back prevention)
            if "current_registration_id" in request.session:
                del request.session["current_registration_id"]
            if get_session_key(link_id) in request.session:
                # Set final session status
                request.session[get_session_key(link_id)] = "submitted"
            request.session.modified = True

        return redirect("test:user_already_submitted")

    # --- GET LOGIC (Rendering Questions - Existing logic retained) ---

    questions = (
        Question.objects.select_related("section")
        .filter(section__question_paper=paper)
        .order_by("section__order", "order")
    )

    sections_with_questions = {}

    for q in questions:
        section_title = q.section.title

        if section_title not in sections_with_questions:
            sections_with_questions[section_title] = {
                "title": section_title,
                "questions": [],
            }

        options_list = q.options if isinstance(q.options, list) else None

        if options_list:
            # उच्च प्राथमिकता: अगर options हैं, तो यह हमेशा MCQ होना चाहिए
            q_type = "MCQ"
        else:
            # अन्यथा, सीधे डेटाबेस में संग्रहीत प्रकार का उपयोग करें
            # (स्ट्रिंग को अपरकेस में बदलने से Consistency बनी रहती है)
            q_type = q.question_type.upper()

        sections_with_questions[section_title]["questions"].append(
            {"id": q.id, "text": q.text, "options": options_list, "type": q_type}
        )

    sections_list = list(sections_with_questions.values())

    context = {
        "paper": paper,
        "sections_list": sections_list,
        "link_id": link_id,
        # "total_duration": paper.duration * 60, <-- REMOVED (now handled by API)
    }
    return render(request, "user_test/test.html", context)


def user_already_submitted_view(request):
    """
    Shows the final 'Response Recorded' screen.
    """
    return render(request, "user_test/already_submitted.html")
