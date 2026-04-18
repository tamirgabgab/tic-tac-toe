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

    if 'board' not in st.session_state:
        st.session_state.board = [0] * 9
        st.session_state.hx = []
        st.session_state.ho = []
        st.session_state.turn = 1
        st.session_state.show_best = False

    def handle_click(i_0):
        if st.session_state.board[i_0] == 0:
            p = st.session_state.turn
            curr_h = st.session_state.hx if p == 1 else st.session_state.ho
            if len(curr_h) >= 3:
                oldest = curr_h.pop(0)
                st.session_state.board[oldest] = 0
            st.session_state.board[i_0] = p
            curr_h.append(i_0)
            st.session_state.turn *= -1

    best = get_best_move(st.session_state.board, st.session_state.hx, st.session_state.ho, st.session_state.turn)
    winner = check_win(st.session_state.board)

    # בנה רשימה של סוגי כפתורים לפני הרינדור
    best_index = best if (winner is None and st.session_state.get('show_best', True)) else -1
    fading_index = -1
    if len(st.session_state.hx) == 3 and st.session_state.turn == 1:
        fading_index = st.session_state.hx[0]
    elif len(st.session_state.ho) == 3 and st.session_state.turn == -1:
        fading_index = st.session_state.ho[0]

    cols = st.columns(3)
    for i in range(9):
        with cols[i % 3]:
            val = st.session_state.board[i]
            label = "X" if val == 1 else ("O" if val == -1 else " ")

            if st.button(label, key=f"btn_{i}", use_container_width=True, type="secondary"):
                handle_click(i)
                st.rerun()

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

        // Streamlit מסדר לפי עמודות - ממיר לסדר שורות
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

    s_trn = 'X' if st.session_state.turn == 1 else 'O'
    st.divider()
    st.markdown(
        f"<p style='text-align:right; font-size:20px; font-weight:600; margin:0 0 4px 0;'>תור השחקן : {s_trn}</p>",
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
        style = (
            "background-color:#d4edda; border:1px solid #c3e6cb; "
            "border-radius:4px; padding:10px 15px; text-align:right; "
            "font-size:16px; color:#155724; margin-bottom:16px;"
        )
        st.markdown(f'<div style="{style}">המנצח הוא: {winner_char} 🏆</div>', unsafe_allow_html=True)
    elif best != -1:
        pass
        # st.info(f"💡 מהלך מומלץ: משבצת {best}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("איפוס משחק", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        label = "הסתר מהלך מומלץ" if st.session_state.get('show_best', True) else "הצג מהלך מומלץ"
        if st.button(label, use_container_width=True):
            st.session_state.show_best = not st.session_state.get('show_best', True)
            st.rerun()


if __name__ == "__main__":
    if not runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        stcli.main()
    else:
        main()