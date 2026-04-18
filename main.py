import streamlit as st
import streamlit.components.v1 as components
from streamlit import runtime
from streamlit.web import cli as stcli
import sys
import math


def check_win(board):
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] != 0:
            return board[a]
    return None


def get_best_move(board, history_x, history_o, player):
    def simulate(b, hx, ho, move, p):
        nb_0, nhx_0, nho_0 = list(b), list(hx), list(ho)
        curr_h = nhx_0 if p == 1 else nho_0
        if len(curr_h) >= 3:
            nb_0[curr_h.pop(0)] = 0
        nb_0[move] = p
        curr_h.append(move)
        return nb_0, nhx_0, nho_0

    def minimax(b, hx, ho, depth, is_max):
        winner = check_win(b)
        if winner == 1:
            return 10 - depth
        if winner == -1:
            return depth - 10
        if depth >= 7:
            return 0
        moves = [i for i, v in enumerate(b) if v == 0]
        if not moves:
            return 0
        if is_max:
            best = -math.inf
            for p_m in moves:
                nb_0, nhx_0, nho_0 = simulate(b, hx, ho, p_m, 1)
                best = max(best, minimax(nb_0, nhx_0, nho_0, depth + 1, False))
            return best
        else:
            best = math.inf
            for p_m in moves:
                nb_0, nhx_0, nho_0 = simulate(b, hx, ho, p_m, -1)
                best = min(best, minimax(nb_0, nhx_0, nho_0, depth + 1, True))
            return best

    best_val = -math.inf if player == 1 else math.inf
    best_move = -1
    for m in [i for i, v in enumerate(board) if v == 0]:
        nb, nhx, nho = simulate(board, history_x, history_o, m, player)
        val = minimax(nb, nhx, nho, 1, player == -1)
        if (player == 1 and val > best_val) or (player == -1 and val < best_val):
            best_val, best_move = val, m
    return best_move


def make_move(board, hx, ho, index, player):
    """ביצוע מהלך על הלוח ועדכון היסטוריה"""
    curr_h = hx if player == 1 else ho
    if len(curr_h) >= 3:
        oldest = curr_h.pop(0)
        board[oldest] = 0
    board[index] = player
    curr_h.append(index)


def main():
    st.set_page_config(page_title="Dynamic Tic-Tac-Toe Solver")
    st.title("איקס עיגול דינמי - פותר אופטימלי")

    st.markdown("""
    <style>
    .stApp { direction: rtl; }
    div.stButton > button {
        height: 80px;
        font-size: 25px !important;
        font-weight: bold;
    }
    h1, h2, h3, p, div, span, label { text-align: right !important; }
    iframe { display: none !important; }
    hr { margin: 0 !important; padding: 0 !important; }
    .block-container { gap: 0 !important; }
    [data-testid="stVerticalBlock"] > div { margin-top: 0 !important; padding-top: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── אתחול session ──────────────────────────────────────────────
    if 'board' not in st.session_state:
        st.session_state.board = [0] * 9
        st.session_state.hx = []
        st.session_state.ho = []
        st.session_state.turn = 1
        st.session_state.show_best = False
        st.session_state.game_mode = 'pvp'   # 'pvp' | 'pvc'
        st.session_state.human_side = 1      # 1=X , -1=O

    # ── בחירת מצב משחק ────────────────────────────────────────────
    st.markdown("### הגדרות משחק")
    mode_col, side_col = st.columns(2)

    with mode_col:
        mode_label = st.radio(
            "מצב משחק",
            options=['pvp', 'pvc'],
            format_func=lambda x: "שחקן נגד שחקן" if x == 'pvp' else "שחקן נגד מחשב",
            index=0 if st.session_state.game_mode == 'pvp' else 1,
            horizontal=True,
            key='mode_radio'
        )
        if mode_label != st.session_state.game_mode:
            st.session_state.game_mode = mode_label
            # איפוס לוח בהחלפת מצב
            st.session_state.board = [0] * 9
            st.session_state.hx = []
            st.session_state.ho = []
            st.session_state.turn = 1
            st.rerun()

    with side_col:
        if st.session_state.game_mode == 'pvc':
            side_label = st.radio(
                "אני משחק בתור",
                options=[1, -1],
                format_func=lambda x: "X (מתחיל ראשון)" if x == 1 else "O (מתחיל שני)",
                index=0 if st.session_state.human_side == 1 else 1,
                horizontal=True,
                key='side_radio'
            )
            if side_label != st.session_state.human_side:
                st.session_state.human_side = side_label
                st.session_state.board = [0] * 9
                st.session_state.hx = []
                st.session_state.ho = []
                st.session_state.turn = 1
                st.rerun()

    st.divider()

    # ── האם זה תור המחשב? ─────────────────────────────────────────
    is_pvc = st.session_state.game_mode == 'pvc'
    computer_side = -st.session_state.human_side  # הצד ההפוך מהאדם
    winner = check_win(st.session_state.board)
    computer_turn = (
        is_pvc
        and winner is None
        and st.session_state.turn == computer_side
    )

    # אם זה תור המחשב – בצע מהלך אוטומטית
    if computer_turn:
        comp_move = get_best_move(
            st.session_state.board,
            st.session_state.hx,
            st.session_state.ho,
            computer_side
        )
        if comp_move != -1:
            make_move(st.session_state.board, st.session_state.hx, st.session_state.ho, comp_move, computer_side)
            st.session_state.turn *= -1
            st.rerun()

    winner = check_win(st.session_state.board)
    best = get_best_move(st.session_state.board, st.session_state.hx, st.session_state.ho, st.session_state.turn)

    # ── צביעת כפתורים (fading / best) ─────────────────────────────
    best_index = best if (winner is None and st.session_state.get('show_best', True)) else -1
    # במצב נגד מחשב אל תציג רמז כשזה תור המחשב
    if is_pvc and st.session_state.turn == computer_side:
        best_index = -1

    fading_index = -1
    if len(st.session_state.hx) == 3 and st.session_state.turn == 1:
        fading_index = st.session_state.hx[0]
    elif len(st.session_state.ho) == 3 and st.session_state.turn == -1:
        fading_index = st.session_state.ho[0]

    # ── לוח המשחק ─────────────────────────────────────────────────
    # חסום לחיצה אם זה תור המחשב
    board_disabled = is_pvc and st.session_state.turn == computer_side

    cols = st.columns(3)
    for i in range(9):
        with cols[i % 3]:
            val = st.session_state.board[i]
            label = "X" if val == 1 else ("O" if val == -1 else " ")
            if st.button(label, key=f"btn_{i}", use_container_width=True, type="secondary", disabled=board_disabled):
                if st.session_state.board[i] == 0 and winner is None:
                    make_move(
                        st.session_state.board,
                        st.session_state.hx,
                        st.session_state.ho,
                        i,
                        st.session_state.turn
                    )
                    st.session_state.turn *= -1
                    st.rerun()

    # ── JavaScript לצבעים ─────────────────────────────────────────
    components.html(f"""
    <script>
    var sessionBest = {best_index};
    var sessionFading = {fading_index};

    function colorButtons() {{
        var allBtns = Array.from(window.parent.document.querySelectorAll('div.stButton > button'));

        var gameBtns = allBtns.filter(function(btn) {{
            var t = btn.innerText.trim();
            return t === 'X' || t === 'O' || t === '' || t === ' ';
        }}).slice(0, 9);

        var colOrder = [0,3,6,1,4,7,2,5,8];
        var orderedBtns = colOrder.map(function(i) {{ return gameBtns[i]; }});

        orderedBtns.forEach(function(btn, count) {{
            if (!btn) return;
            var text = btn.innerText.trim();
            var isFading = (count === sessionFading);
            var isBest = (count === sessionBest);

            if (isFading && text === 'X') {{
                btn.style.setProperty('background-color', '#ffe8e8', 'important');
                btn.style.setProperty('color', '#ffaaaa', 'important');
                btn.style.setProperty('border', '2px solid #ffaaaa', 'important');
            }} else if (isFading && text === 'O') {{
                btn.style.setProperty('background-color', '#e8f4ff', 'important');
                btn.style.setProperty('color', '#aaccff', 'important');
                btn.style.setProperty('border', '2px solid #aaccff', 'important');
            }} else if (isBest) {{
                btn.style.setProperty('background-color', '#f0fff0', 'important');
                btn.style.setProperty('color', '#aaddaa', 'important');
                btn.style.setProperty('border', '2px solid #cceecc', 'important');
                btn.onmouseenter = function() {{
                    btn.style.setProperty('border', '2px solid #88cc88', 'important');
                    btn.style.setProperty('background-color', '#e0ffe0', 'important');
                }};
                btn.onmouseleave = function() {{
                    btn.style.setProperty('border', '2px solid #cceecc', 'important');
                    btn.style.setProperty('background-color', '#f0fff0', 'important');
                }};
            }} else if (text === 'X') {{
                btn.style.setProperty('background-color', '#ffcccc', 'important');
                btn.style.setProperty('color', '#b30000', 'important');
                btn.style.setProperty('border', '2px solid #ff6666', 'important');
            }} else if (text === 'O') {{
                btn.style.setProperty('background-color', '#cce0ff', 'important');
                btn.style.setProperty('color', '#003580', 'important');
                btn.style.setProperty('border', '2px solid #3399ff', 'important');
            }} else {{
                btn.style.removeProperty('background-color');
                btn.style.removeProperty('color');
                btn.style.removeProperty('border');
            }}
        }});
    }}
    colorButtons();
    setTimeout(colorButtons, 300);
    setTimeout(colorButtons, 800);
    new MutationObserver(colorButtons).observe(window.parent.document.body, {{childList: true, subtree: true}});
    </script>
    """, height=1)

    # ── מידע תחתון ────────────────────────────────────────────────
    s_trn = 'X' if st.session_state.turn == 1 else 'O'
    if is_pvc and st.session_state.turn == computer_side:
        turn_label = f"תור המחשב ({s_trn}) 🤖"
    else:
        turn_label = f"תור השחקן: {s_trn}"

    st.divider()
    st.markdown(
        f"<p style='text-align:right; font-size:20px; font-weight:600; margin:0 0 4px 0;'>{turn_label}</p>",
        unsafe_allow_html=True)

    if winner:
        st.balloons()
        components.html("""
        <script>
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        function playTone(freq, start, duration, vol) {
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = freq;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0, ctx.currentTime + start);
            gain.gain.linearRampToValueAtTime(vol, ctx.currentTime + start + 0.01);
            gain.gain.linearRampToValueAtTime(0, ctx.currentTime + start + duration);
            osc.start(ctx.currentTime + start);
            osc.stop(ctx.currentTime + start + duration + 0.05);
        }
        playTone(523, 0.0, 0.15, 0.4);
        playTone(659, 0.15, 0.15, 0.4);
        playTone(784, 0.30, 0.15, 0.4);
        playTone(1047, 0.45, 0.4, 0.5);
        </script>
        """, height=0)
        winner_char = 'X' if winner == 1 else 'O'
        if is_pvc:
            if winner == st.session_state.human_side:
                result_text = f"🏆 כל הכבוד! ניצחת את המחשב! ({winner_char})"
                result_color = "#d4edda"
                border_color = "#c3e6cb"
                text_color = "#155724"
            else:
                result_text = f"🤖 המחשב ניצח! ({winner_char})"
                result_color = "#f8d7da"
                border_color = "#f5c6cb"
                text_color = "#721c24"
        else:
            result_text = f"המנצח הוא: {winner_char} 🏆"
            result_color = "#d4edda"
            border_color = "#c3e6cb"
            text_color = "#155724"

        style = (
            f"background-color:{result_color}; border:1px solid {border_color}; "
            f"border-radius:4px; padding:10px 15px; text-align:right; "
            f"font-size:16px; color:{text_color}; margin-bottom:16px;"
        )
        st.markdown(f'<div style="{style}">{result_text}</div>', unsafe_allow_html=True)

    # ── כפתורי בקרה ───────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if st.button("איפוס משחק", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        if st.session_state.game_mode == 'pvp':
            label = "הסתר מהלך מומלץ" if st.session_state.get('show_best', True) else "הצג מהלך מומלץ"
            if st.button(label, use_container_width=True):
                st.session_state.show_best = not st.session_state.get('show_best', True)
                st.rerun()
        else:
            # במצב נגד מחשב – רמז רלוונטי רק לתור השחקן
            label = "הסתר רמז" if st.session_state.get('show_best', True) else "הצג רמז למהלך"
            if st.button(label, use_container_width=True):
                st.session_state.show_best = not st.session_state.get('show_best', True)
                st.rerun()


if __name__ == "__main__":
    if not runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        stcli.main()
    else:
        main()
