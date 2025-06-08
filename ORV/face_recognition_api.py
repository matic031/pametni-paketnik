import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from api.face_embedder import get_embedding_from_image_bytes
    from user_management.db import (
        register_user_embeddings,
        verify_user_by_embedding,
        is_user_registered,
        delete_user,
        VERIFICATION_THRESHOLD,
    )

    try:
        from face_processing.detection import detect_face
        from face_processing.augmentation import generate_augmented_faces
        from face_processing.embedding_model import (
            initialize_embedding_model,
            get_face_embedding,
            preprocess_face_for_embedding,
        )

        FACE_PROCESSING_AVAILABLE = True
    except ImportError as face_import_error:
        print(f"Warning: Face processing modules not available: {face_import_error}")
        print("Augmentation will be disabled, using single embedding only.")
        FACE_PROCESSING_AVAILABLE = False

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the ORV root directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

print("Initializing face recognition models...")
if FACE_PROCESSING_AVAILABLE:
    initialize_embedding_model()
print("Face recognition API ready!")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "service": "Face Recognition API", "version": "1.0.0"}
    )


@app.route("/register", methods=["POST"])
def register_user_face():
    """
    Register user with face embeddings
    Expects: user_id and image file
    """
    try:
        user_id = request.form.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "user_id is required"}), 400

        if is_user_registered(user_id):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "User already registered. Use update endpoint to modify.",
                    }
                ),
                409,
            )

        if "image" not in request.files:
            return jsonify({"success": False, "message": "No image file provided"}), 400

        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"success": False, "message": "No image file selected"}), 400

        image_bytes = image_file.read()

        embedding_result = get_embedding_from_image_bytes(image_bytes)
        if embedding_result is None:
            return (
                jsonify({"success": False, "message": "No face detected in image"}),
                400,
            )

        embedding = (
            embedding_result[0]
            if isinstance(embedding_result, tuple)
            else embedding_result
        )

        if FACE_PROCESSING_AVAILABLE:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            face_roi, face_coords = detect_face(img_bgr)
            if face_roi is None:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "No face detected for augmentation",
                        }
                    ),
                    400,
                )

            face_processed = preprocess_face_for_embedding(face_roi)
            if face_processed is None:
                return (
                    jsonify({"success": False, "message": "Failed to preprocess face"}),
                    400,
                )

            try:
                augmented_faces = generate_augmented_faces(face_processed)
                embeddings_list = []

                embeddings_list.append(embedding)

                for aug_face in augmented_faces:
                    aug_embedding = get_face_embedding(aug_face)
                    if aug_embedding is not None:
                        embeddings_list.append(aug_embedding)

                if len(embeddings_list) == 0:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Failed to generate any embeddings",
                            }
                        ),
                        400,
                    )

                embeddings_np = [
                    np.array(emb, dtype=np.float32) for emb in embeddings_list
                ]

                register_user_embeddings(user_id, embeddings_np)

                return jsonify(
                    {
                        "success": True,
                        "message": f"User {user_id} registered successfully",
                        "embeddings_count": len(embeddings_np),
                    }
                )

            except Exception as e:
                print(f"Error during augmentation: {e}")
                embeddings_np = [np.array(embedding, dtype=np.float32)]
                register_user_embeddings(user_id, embeddings_np)

                return jsonify(
                    {
                        "success": True,
                        "message": f"User {user_id} registered with single embedding (augmentation failed)",
                        "embeddings_count": 1,
                    }
                )
        else:
            embeddings_np = [np.array(embedding, dtype=np.float32)]
            register_user_embeddings(user_id, embeddings_np)

            return jsonify(
                {
                    "success": True,
                    "message": f"User {user_id} registered with single embedding",
                    "embeddings_count": 1,
                }
            )

    except Exception as e:
        print(f"Registration error: {e}")
        return (
            jsonify({"success": False, "message": f"Registration failed: {str(e)}"}),
            500,
        )


@app.route("/verify", methods=["POST"])
def verify_user_face():
    """
    Verify user with face image
    Expects: user_id and image file
    """
    try:
        user_id = request.form.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "user_id is required"}), 400

        if not is_user_registered(user_id):
            return jsonify({"success": False, "message": "User not registered"}), 404

        if "image" not in request.files:
            return jsonify({"success": False, "message": "No image file provided"}), 400

        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"success": False, "message": "No image file selected"}), 400

        image_bytes = image_file.read()

        embedding = get_embedding_from_image_bytes(image_bytes)
        if embedding is None:
            return (
                jsonify({"success": False, "message": "No face detected in image"}),
                400,
            )

        is_verified, similarity_score = verify_user_by_embedding(user_id, embedding[0])

        return jsonify(
            {
                "success": True,
                "verified": is_verified,
                "similarity_score": float(similarity_score),
                "threshold": VERIFICATION_THRESHOLD,
                "message": (
                    "Verification successful" if is_verified else "Verification failed"
                ),
            }
        )

    except Exception as e:
        print(f"Verification error: {e}")
        return (
            jsonify({"success": False, "message": f"Verification failed: {str(e)}"}),
            500,
        )


@app.route("/user/<user_id>", methods=["GET"])
def get_user_info(user_id):
    """Get user registration status"""
    try:
        is_registered = is_user_registered(user_id)
        return jsonify(
            {"success": True, "user_id": user_id, "is_registered": is_registered}
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error checking user: {str(e)}"}),
            500,
        )


@app.route("/user/<user_id>", methods=["DELETE"])
def delete_user_face(user_id):
    """Delete user face registration"""
    try:
        if not is_user_registered(user_id):
            return jsonify({"success": False, "message": "User not registered"}), 404

        delete_user(user_id)
        return jsonify(
            {"success": True, "message": f"User {user_id} deleted successfully"}
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error deleting user: {str(e)}"}),
            500,
        )


@app.route("/", methods=["GET"])
def index():
    """API documentation"""
    return jsonify(
        {
            "service": "Face Recognition API",
            "version": "1.0.0",
            "endpoints": {
                "POST /register": "Register user with face image (multipart/form-data: user_id, image)",
                "POST /verify": "Verify user with face image (multipart/form-data: user_id, image)",
                "GET /user/<user_id>": "Get user registration status",
                "DELETE /user/<user_id>": "Delete user registration",
                "GET /health": "Health check",
            },
        }
    )


if __name__ == "__main__":
    print("Starting Face Recognition API server...")
    print("Available endpoints:")
    print("  POST /register - Register user with face")
    print("  POST /verify - Verify user with face")
    print("  GET /user/<user_id> - Get user status")
    print("  DELETE /user/<user_id> - Delete user")
    print("  GET /health - Health check")

    app.run(host="0.0.0.0", port=5000, debug=True)
