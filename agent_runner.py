from crewai import Agent, Task, Crew
import os
import traceback

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def run_agent_analysis(
    datos,
    resumen_preprocesado="",
    rol="Analista AI",
    objetivo="Analizar datos y generar insights útiles",
    backstory="Un experto en análisis de datos",
    prompt_extra="Analiza la siguiente información y devuelve hallazgos valiosos.",
    modelo="gpt-4",
    verbose=True
):
    try:
        # Armar agente
        agente = Agent(
            role=rol,
            goal=objetivo,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=False,
            llm_config={
                "api_key": OPENAI_API_KEY,
                "model": modelo
            }
        )

        # Descripción completa
        task_description = (
            f"{prompt_extra}\n\n"
            f"{resumen_preprocesado}\n\n"
            f"Datos completos:\n{datos}"
        )

        # Armar tarea
        tarea = Task(
            description=task_description,
            expected_output="Análisis conciso y accionable sobre los datos.",
            agent=agente
        )

        # Ejecutar Crew
        crew = Crew(agents=[agente], tasks=[tarea], verbose=2)
        resultado = crew.kickoff()
        return resultado

    except Exception as e:
        print("❌ Error en run_agent_analysis:")
        traceback.print_exc()
        return f"Error: {str(e)}"

