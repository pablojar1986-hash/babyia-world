from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def log_start():
    console.print(Panel(
        "[bold cyan]BabyIA World 0.1[/bold cyan]\n"
        "[dim]IA que aprende desde cero · sin APIs externas · solo experiencia[/dim]",
        border_style="cyan",
    ))


def log_episode_start(episode, level):
    console.print(f"\n[bold cyan]▶ Episodio {episode}[/bold cyan]  Nivel {level}")


def log_event(step, action_name, hit_wall, reached_goal):
    if reached_goal:
        console.print(f"  [bold green]✓ META alcanzada en paso {step}[/bold green]")
    elif hit_wall:
        console.print(f"  [red]✗ Choque  paso={step}  acción={action_name}[/red]")


def log_episode_end(status):
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("k", style="dim", no_wrap=True)
    t.add_column("v")

    em = status["emotions"]
    t.add_row("Recompensa ep", f"{status['episode_reward']:+.2f}")
    t.add_row("ε exploración", f"{status['epsilon']:.3f}")
    t.add_row("Éxito 20ep",    f"{status['success_rate']*100:.0f}%")
    t.add_row("Curiosidad",    f"{em['curiosity']:.2f}")
    t.add_row("Confianza",     f"{em['confidence']:.2f}")
    t.add_row("Frustración",   f"{em['frustration']:.2f}")
    t.add_row("Loss",          f"{status['loss']:.4f}")

    console.print(Panel(t, title=f"[bold]Ep {status['episode']}[/bold]", border_style="blue"))

    if status["last_log"]:
        console.print(f"[italic dim]{status['last_log'][-1]}[/italic dim]")


def log_level_up(new_level):
    msgs = {
        1: "Aprende a llegar a la meta",
        2: "Aprende a evitar paredes",
        3: "Empieza a formar conceptos",
    }
    console.print(Panel(
        f"[bold green]¡BabyIA subió al Nivel {new_level}![/bold green]\n"
        f"[dim]{msgs.get(new_level, '')}[/dim]",
        border_style="green",
    ))
