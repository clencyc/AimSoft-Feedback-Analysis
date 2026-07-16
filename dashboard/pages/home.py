import base64
from pathlib import Path
import base64

import streamlit as st


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("assets/aimsoftlogo.png")
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ILLUSTRATION_PATH = ASSETS_DIR / "homepage_illustration.jpg"


def _image_base64(path: Path):
	if not path.exists():
		return None
	return base64.b64encode(path.read_bytes()).decode()


def render_home():
	st.markdown(
		"""
		<style>
			.navbar {
				display: flex;
				align-items: center;
				justify-content: space-between;
				
			}
			.navbar .brand {
				font-weight: 800;
				font-size: 1.35rem;
				color: #0f172a;
			}
			.navbar .links {
				display: flex;
				gap: 1.8rem;
				color: #475569;
				font-size: 0.95rem;
			}
			.headline {
				font-size: 2.9rem;
				font-weight: 800;
				line-height: 1.12;
				color: #0f172a;
				margin: 0;
			}
			.subtext {
				font-size: 1.08rem;
				color: #475569;
				margin: 1.2rem 0 1.6rem;
				max-width: 480px;
			}
			.illustration-wrap {
				position: relative;
				border-radius: 28px;
				overflow: hidden;
				min-height: 440px;
				box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
			}
			.illustration-bg {
				position: absolute;
				inset: 0;
				background: linear-gradient(160deg, #fb923c 0%, #fb923c 52%, #34d399 52%, #34d399 100%);
			}
			.illustration-img {
				position: relative;
				z-index: 1;
				width: 100%;
				height: 100%;
				object-fit: contain;
				padding: 2.2rem;
				display: block;
			}
		</style>
		""",
		unsafe_allow_html=True,
	)

	st.markdown(
		f"""
        <style>
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            color: #111111;
        }}
        .brand-logo {{
            height: 42px;
            width: auto;
        }}
        </style>
        
        <div class="navbar">
            <div class="brand">
                <img src="data:image/png;base64,{logo_base64}" class="brand-logo">
                AimSoft
            </div>
        </div>
        """,
        unsafe_allow_html=True,
	)

	left, right = st.columns([1.05, 1], vertical_alignment="center")

	with left:
		st.markdown(
			"""
			<h1 class="headline">Feedback that speaks<br/>your customers'<br/>language</h1>
			<p class="subtext">
				Multi-channel sentiment analysis for East African insurers —
				see what customers are really saying, in one dashboard.
			</p>
			""",
			unsafe_allow_html=True,
		)
		if st.button("Get Started →", type="primary"):
			st.session_state.view = "login"
			st.rerun()
		st.caption(
			"Sign in with the credentials your admin gave you — you'll land on "
			"the dashboard built for your team."
		)

	with right:
		img_b64 = _image_base64(ILLUSTRATION_PATH)
		if img_b64:
			st.markdown(
				f"""
				<div class="illustration-wrap">
					<div class="illustration-bg"></div>
					<img class="illustration-img" src="data:image/jpeg;base64,{img_b64}" />
				</div>
				""",
				unsafe_allow_html=True,
			)
		else:
			st.info(
				f"Illustration not found at {ILLUSTRATION_PATH}. "
				"Drop your image there to show it here."
			)


render_home()