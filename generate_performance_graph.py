# generate_performance_graph.py
import matplotlib.pyplot as plt

def generate_performance_chart(data):
    """
    Génère un graphique de performance basé sur les données du fonds.
    
    Args:
        data (list): Liste de dictionnaires avec des données sur la performance du fonds.
        
    Returns:
        str: Le chemin du fichier image contenant le graphique généré.
    """
    dates = [entry['date'] for entry in data]
    performance_values = [entry['performance'] for entry in data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, performance_values, marker='o', color='b', label="Performance du Fonds")
    plt.title("Performance du Fonds au Fil du Temps")
    plt.xlabel("Date")
    plt.ylabel("Performance (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    chart_path = "performance_chart.png"
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path
