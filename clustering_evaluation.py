# ═════════════════════════════════════════════════════════════════════════════
# MÓDULO DE EVALUACIÓN DE CLUSTERING
# ═════════════════════════════════════════════════════════════════════════════
"""
Funciones para evaluación rigurosa de clustering con métricas internas y clínicas.

Métricas Internas (sin etiquetas):
  - Silhouette Score: -1 a 1 (mayor = mejor)
  - Davies-Bouldin Index: 0 a ∞ (menor = mejor)
  - Calinski-Harabasz Index: 0 a ∞ (mayor = mejor)

Métricas Clínicas (vs riesgo MINSA):
  - Adjusted Rand Index (ARI): -1 a 1 (mayor = mejor coincidencia)
  - Fowlkes-Mallows Index: 0 a 1 (mayor = mejor)

Autor: Arnold Zamoratec
Versión: 2.1
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
    silhouette_samples, adjusted_rand_score, fowlkes_mallows_score
)

logger = logging.getLogger(__name__)

PALETTE = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4', '#91D1C2']


# ═════════════════════════════════════════════════════════════════════════════
# 1. EVALUACIÓN DE UN ALGORITMO
# ═════════════════════════════════════════════════════════════════════════════

def evaluate_clustering_algorithm(algo_name, model, X_train, X_test, y_risk_test,
                                   df_train=None, df_test=None):
    """
    Evalúa un algoritmo de clustering completamente.
    
    Retorna:
        dict con todas las métricas y artefactos
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 EVALUANDO: {algo_name}")
    logger.info(f"{'='*70}")
    
    # Entrenar
    clusters_train = model.fit_predict(X_train)
    clusters_test = model.predict(X_test) if hasattr(model, 'predict') else clusters_train
    
    # Métricas internas
    silh_train = silhouette_score(X_train, clusters_train)
    silh_test = silhouette_score(X_test, clusters_test)
    db_test = davies_bouldin_score(X_test, clusters_test)
    ch_test = calinski_harabasz_score(X_test, clusters_test)
    
    # Métricas clínicas
    ari = adjusted_rand_score(y_risk_test, clusters_test)
    fm = fowlkes_mallows_score(y_risk_test, clusters_test)
    
    # Información de clusters
    n_clusters = len(set(clusters_test)) - (1 if -1 in clusters_test else 0)
    n_noise = list(clusters_test).count(-1) if -1 in clusters_test else 0
    
    # Log
    logger.info(f"  Silhouette:       Train={silh_train:6.3f} | Test={silh_test:6.3f}")
    logger.info(f"  Davies-Bouldin:   {db_test:6.3f} (menor = mejor)")
    logger.info(f"  Calinski-Harabasz: {ch_test:8.1f} (mayor = mejor)")
    logger.info(f"  ARI (clínico):    {ari:6.3f} {'✅' if ari > 0.15 else '⚠️'}")
    logger.info(f"  Fowlkes-Mallows:  {fm:6.3f}")
    logger.info(f"  Clusters: {n_clusters} | Ruido: {n_noise}")
    
    return {
        'algorithm': algo_name,
        'model': model,
        'clusters_train': clusters_train,
        'clusters_test': clusters_test,
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'silhouette_train': silh_train,
        'silhouette_test': silh_test,
        'davies_bouldin_test': db_test,
        'calinski_harabasz_test': ch_test,
        'ari': ari,
        'fowlkes_mallows': fm,
        'labels_test': clusters_test
    }


# ═════════════════════════════════════════════════════════════════════════════
# 2. COMPARACIÓN DE ALGORITMOS
# ═════════════════════════════════════════════════════════════════════════════

def compare_algorithms(results_list):
    """
    Compara múltiples algoritmos y selecciona el mejor.
    
    Args:
        results_list: Lista de dicts retornados por evaluate_clustering_algorithm
    
    Returns:
        (df_comparison, best_algorithm_dict)
    """
    logger.info(f"\n{'='*70}")
    logger.info("📊 COMPARACIÓN DE ALGORITMOS")
    logger.info(f"{'='*70}")
    
    # Crear tabla
    data = []
    for result in results_list:
        data.append({
            'Algorithm': result['algorithm'],
            'Silhouette': result['silhouette_test'],
            'Davies-Bouldin': result['davies_bouldin_test'],
            'Calinski-Harabasz': result['calinski_harabasz_test'],
            'ARI (Clinical)': result['ari'],
            'Fowlkes-Mallows': result['fowlkes_mallows'],
            'N_Clusters': result['n_clusters'],
            'N_Noise': result['n_noise']
        })
    
    df_comparison = pd.DataFrame(data)
    
    # Seleccionar ganador (máximo ARI)
    best_idx = df_comparison['ARI (Clinical)'].idxmax()
    best_algorithm = results_list[best_idx]
    
    # Log
    print("\n" + df_comparison.to_string(index=False))
    
    logger.info(f"\n🏆 GANADOR: {best_algorithm['algorithm']}")
    logger.info(f"   ARI: {best_algorithm['ari']:.3f}")
    logger.info(f"   Silhouette: {best_algorithm['silhouette_test']:.3f}")
    
    return df_comparison, best_algorithm


# ═════════════════════════════════════════════════════════════════════════════
# 3. VISUALIZACIONES
# ═════════════════════════════════════════════════════════════════════════════

def plot_silhouette_analysis(X_test, clusters_test, algo_name, save_path=None):
    """Gráfico de análisis silhouette detallado."""
    silh_samples = silhouette_samples(X_test, clusters_test)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    y_lower = 10
    for i in np.unique(clusters_test):
        cluster_silh = silh_samples[clusters_test == i]
        cluster_silh.sort()
        
        ax.fill_betweenx(np.arange(y_lower, y_lower + len(cluster_silh)),
                         0, cluster_silh, alpha=0.7, label=f'Cluster {i}')
        y_lower += len(cluster_silh) + 10
    
    ax.set_xlabel('Silhouette Coefficient')
    ax.set_ylabel('Cluster')
    ax.set_title(f'Silhouette Analysis - {algo_name}', fontsize=12, weight='bold')
    ax.axvline(silh_samples.mean(), color='red', linestyle='--', label='Media')
    ax.legend()
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.show()


def plot_comparison_table(df_comparison, save_path=None):
    """Tabla visual de comparación de algoritmos."""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')
    
    # Crear tabla
    table_data = []
    for idx, row in df_comparison.iterrows():
        table_data.append([
            row['Algorithm'],
            f"{row['Silhouette']:.3f}",
            f"{row['Davies-Bouldin']:.3f}",
            f"{row['Calinski-Harabasz']:.1f}",
            f"{row['ARI (Clinical)']:.3f}",
            f"{row['N_Clusters']}",
        ])
    
    columns = ['Algorithm', 'Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz', 'ARI', 'Clusters']
    table = ax.table(cellText=table_data, colLabels=columns, cellLoc='center', loc='center',
                     colWidths=[0.15, 0.12, 0.15, 0.15, 0.12, 0.10])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Colorear encabezado
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#4DBBD5')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Colorear mejor ARI
    best_row = df_comparison['ARI (Clinical)'].idxmax() + 1
    for i in range(len(columns)):
        table[(best_row, i)].set_facecolor('#90EE90')
    
    plt.title('Comparación de Algoritmos de Clustering', fontsize=13, weight='bold', pad=20)
    
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.show()


# ═════════════════════════════════════════════════════════════════════════════
# 4. INTERPRETACIÓN CLÍNICA
# ═════════════════════════════════════════════════════════════════════════════

def analyze_cluster_characteristics(df_test, clusters, selected_features):
    """
    Analiza características de cada cluster.
    
    Retorna:
        dict con perfiles por cluster
    """
    df_analysis = df_test.copy()
    df_analysis['cluster'] = clusters
    
    profiles = {}
    
    for cluster_id in sorted(df_analysis['cluster'].unique()):
        cluster_data = df_analysis[df_analysis['cluster'] == cluster_id]
        
        profile = {
            'n': len(cluster_data),
            'pct': len(cluster_data) / len(df_analysis) * 100,
            'features': {}
        }
        
        for feat in selected_features:
            if feat in cluster_data.columns and cluster_data[feat].dtype in [np.float64, np.int64]:
                profile['features'][feat] = {
                    'mean': cluster_data[feat].mean(),
                    'std': cluster_data[feat].std(),
                    'median': cluster_data[feat].median()
                }
        
        profiles[cluster_id] = profile
    
    return profiles
