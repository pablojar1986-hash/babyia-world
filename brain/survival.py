"""
Evaluador de supervivencia funcional de BabyIA World 0.4.2.
Calcula riesgo, necesidades y recomendaciones basadas en estado corporal,
energia y contexto del mundo. No representa miedo ni deseo real —
es calculo funcional de riesgo y utilidad.
"""


class SurvivalEvaluator:
    """
    Evalua el estado de supervivencia funcional de BabyIA.
    El resultado se usa como contexto en get_status() y en paneles visuales.
    No interfiere con el DQN — es solo diagnostico.
    """

    def evaluate(self, body_state, inventory, world_manager) -> dict:
        """
        Devuelve dict con risk_level, recommendation, should_return_home,
        needs_food y danger_without_protection.
        """
        energy = inventory.energy
        shield = body_state.shield
        fire_imm = body_state.fire_immunity
        poison_imm = body_state.poison_immunity

        needs_food = energy < 0.3

        should_return = False
        is_at_home = True
        try:
            is_at_home = world_manager.is_at_home
            if hasattr(world_manager, "should_return_home"):
                should_return = world_manager.should_return_home()
        except Exception:
            pass

        # Falta de proteccion activa
        protection_score = (
            float(shield > 0.1) + float(fire_imm) + float(poison_imm)
        ) / 3.0
        danger_without_protection = energy < 0.5 and protection_score < 0.3

        # Nivel de riesgo: combina energia baja, falta de proteccion y mundo
        risk_level = max(
            0.0,
            min(
                1.0,
                (1.0 - energy) * 0.4
                + (1.0 - protection_score) * 0.3
                + (0.3 if danger_without_protection else 0.0),
            ),
        )

        # Recomendacion funcional
        if needs_food and not is_at_home:
            recommendation = "buscar_comida_o_regresar"
        elif should_return:
            recommendation = "regresar_a_casa"
        elif danger_without_protection and risk_level > 0.5:
            recommendation = "evitar_peligros"
        elif shield > 0.1:
            recommendation = "puede_cruzar_espinas"
        elif fire_imm and not is_at_home:
            recommendation = "puede_cruzar_fuego"
        elif poison_imm and not is_at_home:
            recommendation = "puede_cruzar_veneno"
        else:
            recommendation = "continuar"

        return {
            "risk_level": round(risk_level, 3),
            "recommendation": recommendation,
            "should_return_home": should_return,
            "needs_food": needs_food,
            "danger_without_protection": danger_without_protection,
        }
