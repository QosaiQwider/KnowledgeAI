import httpx

from google import genai
from google.genai import errors
from groq import Groq

from database.config import GEMINI_API_KEY, GROQ_API_KEY


# =========================================================
# CHECK API KEYS
# =========================================================

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found. Check your .env file."
    )

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. Check your .env file."
    )


# =========================================================
# CLIENTS
# =========================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# GEMINI MODELS
# =========================================================

GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
]


# =========================================================
# GROQ FALLBACK MODEL
# =========================================================

GROQ_MODEL = "openai/gpt-oss-120b"


# =========================================================
# TRY GEMINI
# =========================================================

def try_gemini(prompt: str):

    for model_name in GEMINI_MODELS:

        print(
            f"Trying Gemini model: {model_name}"
        )

        try:

            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response.text:

                print(
                    f"Gemini response received from: "
                    f"{model_name}"
                )

                return response.text

        # -------------------------------------------------
        # Gemini server error
        # مثل 503 Busy
        # -------------------------------------------------

        except errors.ServerError as e:

            print(
                f"Gemini server error on "
                f"{model_name}: {e.code}"
            )

            print(
                "Trying next Gemini model..."
            )

            continue

        # -------------------------------------------------
        # Gemini client error
        # مثل model unavailable / 404
        # -------------------------------------------------

        except errors.ClientError as e:

            print(
                f"Gemini model unavailable: "
                f"{model_name}"
            )

            print(
                "Trying next Gemini model..."
            )

            continue

        # -------------------------------------------------
        # Network error
        # -------------------------------------------------

        except (
            httpx.ConnectError,
            httpx.TimeoutException
        ) as e:

            print(
                f"Gemini connection error: {e}"
            )

            print(
                "Trying next Gemini model..."
            )

            continue

        # -------------------------------------------------
        # Unknown error
        # -------------------------------------------------

        except Exception as e:

            print(
                f"Unexpected Gemini error "
                f"with {model_name}: {e}"
            )

            print(
                "Trying next Gemini model..."
            )

            continue


    # جميع موديلات Gemini فشلت
    return None


# =========================================================
# TRY GROQ
# =========================================================

def try_groq(prompt: str):

    print(
        "All Gemini models failed."
    )

    print(
        f"Trying Groq fallback: {GROQ_MODEL}"
    )

    try:

        response = groq_client.chat.completions.create(

            model=GROQ_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )

        answer = response.choices[0].message.content

        if answer:

            print(
                f"Groq response received from: "
                f"{GROQ_MODEL}"
            )

            return answer

        return None

    except Exception as e:

        print(
            f"Groq fallback failed: {e}"
        )

        raise RuntimeError(
            "Gemini and Groq are currently unavailable."
        ) from e


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(prompt: str):

    if not prompt or not prompt.strip():
        return None

    # =====================================================
    # 1. GEMINI FIRST
    # =====================================================

    answer = try_gemini(prompt)

    if answer:
        return answer


    # =====================================================
    # 2. GROQ FALLBACK
    # =====================================================

    answer = try_groq(prompt)

    if answer:
        return answer


    # =====================================================
    # 3. EVERYTHING FAILED
    # =====================================================

    raise RuntimeError(
        "No LLM provider returned an answer."
    )