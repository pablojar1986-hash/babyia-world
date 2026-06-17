"""Tests 0.4.4: StrategyTracker detecta estrategias de progreso de nivel."""

from brain.strategy import StrategyTracker, KNOWN_STRATEGIES


class TestKnownStrategies:
    def test_progress_strategies_in_known(self):
        expected = [
            "completar_nivel_con_llave",
            "buscar_llave_y_luego_puerta_dorada",
            "ignorar_puertas_opcionales_sin_llave",
            "evitar_peligro_sin_proteccion",
        ]
        for s in expected:
            assert s in KNOWN_STRATEGIES, f"Falta estrategia: {s}"


class TestStrategyTrackerLevelCompleted:
    def test_level_completed_registers_completar_nivel(self):
        st = StrategyTracker()
        st.observe({"level_completed": True}, [])
        assert "completar_nivel_con_llave" in st.active

    def test_level_completed_with_key_registers_buscar_llave_y_puerta(self):
        st = StrategyTracker()
        st.observe({"level_completed": True, "picked_key": True}, [])
        assert "buscar_llave_y_luego_puerta_dorada" in st.active

    def test_level_completed_without_key_event_no_buscar_llave(self):
        st = StrategyTracker()
        st.observe({"level_completed": True}, [])
        assert "buscar_llave_y_luego_puerta_dorada" not in st.active

    def test_level_completed_no_treasure_room_registers_ignorar(self):
        st = StrategyTracker()
        st.observe({"level_completed": True}, [])
        assert "ignorar_puertas_opcionales_sin_llave" in st.active

    def test_level_completed_with_treasure_room_no_ignorar(self):
        st = StrategyTracker()
        st.observe({"level_completed": True, "entered_treasure_room": True}, [])
        assert "ignorar_puertas_opcionales_sin_llave" not in st.active

    def test_no_danger_and_completed_registers_evitar_peligro(self):
        st = StrategyTracker()
        st.observe({"level_completed": True, "in_danger": False}, [])
        assert "evitar_peligro_sin_proteccion" in st.active

    def test_in_danger_and_completed_no_evitar_peligro(self):
        st = StrategyTracker()
        st.observe({"level_completed": True, "in_danger": True}, [])
        assert "evitar_peligro_sin_proteccion" not in st.active


class TestStrategyTrackerAccumulation:
    def test_strategies_accumulate_count(self):
        st = StrategyTracker()
        for _ in range(3):
            st.observe({"level_completed": True}, [])
        assert st.active.get("completar_nivel_con_llave") == 3

    def test_top_returns_most_frequent(self):
        st = StrategyTracker()
        for _ in range(5):
            st.observe({"level_completed": True}, [])
        for _ in range(2):
            st.observe({"level_completed": True, "picked_key": True}, [])
        top = st.top(1)
        assert top[0][0] == "completar_nivel_con_llave"

    def test_to_dict_contains_strategies(self):
        st = StrategyTracker()
        st.observe({"level_completed": True}, [])
        d = st.to_dict()
        assert "strategies" in d
        assert isinstance(d["strategies"], dict)

    def test_no_strategies_without_events(self):
        st = StrategyTracker()
        st.observe({}, [])
        assert "completar_nivel_con_llave" not in st.active
