import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import joblib
import os

class EducationalMLPipeline:
    """Pipeline completo de Machine Learning para dados educacionais."""
    
    def __init__(self):
        self.models = {
            'SVM': SVC(kernel='rbf', random_state=42),
            'Naive_Bayes': GaussianNB(),
            'Decision_Tree': DecisionTreeClassifier(random_state=42, max_depth=10)
        }
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.trained_models = {}
        self.results = {}
        
    def create_sample_educational_dataset(self) -> pd.DataFrame:
        """
        Cria um dataset educacional de exemplo para demonstração.
        
        Returns:
            pd.DataFrame: Dataset com características de estudantes e performance
        """
        np.random.seed(42)
        n_samples = 1000
        
        # Características dos estudantes
        data = {
            'study_hours_per_week': np.random.normal(15, 5, n_samples),
            'previous_score': np.random.normal(75, 15, n_samples),
            'attendance_rate': np.random.normal(85, 10, n_samples),
            'homework_completion': np.random.normal(80, 15, n_samples),
            'participation_score': np.random.normal(70, 20, n_samples),
            'difficulty_preference': np.random.choice(['easy', 'medium', 'hard'], n_samples),
            'learning_style': np.random.choice(['visual', 'auditory', 'kinesthetic'], n_samples),
            'age': np.random.randint(16, 25, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Garantir valores realistas
        df['study_hours_per_week'] = np.clip(df['study_hours_per_week'], 1, 40)
        df['previous_score'] = np.clip(df['previous_score'], 0, 100)
        df['attendance_rate'] = np.clip(df['attendance_rate'], 50, 100)
        df['homework_completion'] = np.clip(df['homework_completion'], 0, 100)
        df['participation_score'] = np.clip(df['participation_score'], 0, 100)
        
        # Criar variável target baseada em lógica educacional
        def calculate_performance(row):
            score = (
                row['study_hours_per_week'] * 0.3 +
                row['previous_score'] * 0.25 +
                row['attendance_rate'] * 0.2 +
                row['homework_completion'] * 0.15 +
                row['participation_score'] * 0.1
            )
            
            if score >= 80:
                return 'excellent'
            elif score >= 65:
                return 'good'
            elif score >= 50:
                return 'average'
            else:
                return 'needs_improvement'
        
        df['performance'] = df.apply(calculate_performance, axis=1)
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Pré-processa os dados educacionais.
        
        Args:
            df: DataFrame com os dados
            
        Returns:
            Tuple com features (X) e target (y) processados
        """
        print("Iniciando pré-processamento dos dados...")
        
        # Separar features categóricas e numéricas
        categorical_features = ['difficulty_preference', 'learning_style']
        numerical_features = ['study_hours_per_week', 'previous_score', 'attendance_rate', 
                             'homework_completion', 'participation_score', 'age']
        
        # Codificar variáveis categóricas
        df_processed = df.copy()
        for feature in categorical_features:
            le = LabelEncoder()
            df_processed[feature + '_encoded'] = le.fit_transform(df_processed[feature])
        
        # Selecionar features para o modelo
        feature_columns = numerical_features + [f + '_encoded' for f in categorical_features]
        X = df_processed[feature_columns].values
        
        # Preparar target
        y = self.label_encoder.fit_transform(df_processed['performance'])
        
        # Normalizar features numéricas
        X = self.scaler.fit_transform(X)
        
        print(f"Dados pré-processados: {X.shape[0]} amostras, {X.shape[1]} features")
        print(f"Classes target: {list(self.label_encoder.classes_)}")
        
        return X, y
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Treina todos os modelos de ML.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Dict com resultados do treinamento
        """
        print("Iniciando treinamento dos modelos...")
        
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        results = {}
        
        for name, model in self.models.items():
            print(f"Treinando {name}...")
            
            # Treinar modelo
            model.fit(X_train, y_train)
            
            # Fazer predições
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            # Armazenar resultados
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'y_test': y_test,
                'y_pred': y_pred,
                'classification_report': classification_report(y_test, y_pred, 
                                                             target_names=self.label_encoder.classes_),
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            }
            
            print(f"{name} - Acurácia: {accuracy:.4f}, F1-Score: {f1:.4f}")
        
        self.trained_models = results
        return results
    
    def evaluate_models(self) -> None:
        """Avalia e compara os modelos treinados."""
        print("\n=== AVALIAÇÃO DETALHADA DOS MODELOS ===")
        
        # Criar DataFrame para comparação
        comparison_data = []
        for name, result in self.trained_models.items():
            comparison_data.append({
                'Modelo': name,
                'Acurácia': result['accuracy'],
                'F1-Score': result['f1_score'],
                'CV Média': result['cv_mean'],
                'CV Desvio': result['cv_std']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Acurácia', ascending=False)
        
        print("\nComparação dos Modelos:")
        print(comparison_df.to_string(index=False))
        
        # Relatórios detalhados
        for name, result in self.trained_models.items():
            print(f"\n--- {name} ---")
            print("Relatório de Classificação:")
            print(result['classification_report'])
    
    def plot_results(self, save_path: str = None) -> None:
        """
        Gera visualizações dos resultados.
        
        Args:
            save_path: Caminho para salvar os gráficos
        """
        if not self.trained_models:
            print("Nenhum modelo treinado encontrado!")
            return
        
        # Configurar matplotlib para português
        plt.rcParams['font.size'] = 12
        
        # Criar subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Avaliação dos Algoritmos de Machine Learning', fontsize=16, fontweight='bold')
        
        # 1. Comparação de Acurácia
        models = list(self.trained_models.keys())
        accuracies = [self.trained_models[m]['accuracy'] for m in models]
        f1_scores = [self.trained_models[m]['f1_score'] for m in models]
        
        axes[0, 0].bar(models, accuracies, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[0, 0].set_title('Comparação de Acurácia')
        axes[0, 0].set_ylabel('Acurácia')
        axes[0, 0].set_ylim(0, 1)
        for i, v in enumerate(accuracies):
            axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # 2. Comparação de F1-Score
        axes[0, 1].bar(models, f1_scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[0, 1].set_title('Comparação de F1-Score')
        axes[0, 1].set_ylabel('F1-Score')
        axes[0, 1].set_ylim(0, 1)
        for i, v in enumerate(f1_scores):
            axes[0, 1].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # 3. Cross-Validation Scores
        cv_means = [self.trained_models[m]['cv_mean'] for m in models]
        cv_stds = [self.trained_models[m]['cv_std'] for m in models]
        
        axes[1, 0].bar(models, cv_means, yerr=cv_stds, color=['#FF6B6B', '#4ECDC4', '#45B7D1'], 
                       capsize=5, alpha=0.7)
        axes[1, 0].set_title('Cross-Validation Scores')
        axes[1, 0].set_ylabel('CV Score')
        axes[1, 0].set_ylim(0, 1)
        
        # 4. Matriz de Confusão do melhor modelo
        best_model = max(self.trained_models.keys(), 
                        key=lambda x: self.trained_models[x]['accuracy'])
        cm = self.trained_models[best_model]['confusion_matrix']
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=self.label_encoder.classes_,
                   yticklabels=self.label_encoder.classes_,
                   ax=axes[1, 1])
        axes[1, 1].set_title(f'Matriz de Confusão - {best_model}')
        axes[1, 1].set_xlabel('Predito')
        axes[1, 1].set_ylabel('Real')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo em: {save_path}")
        
        plt.show()
    
    def save_models(self, directory: str) -> None:
        """
        Salva os modelos treinados.
        
        Args:
            directory: Diretório para salvar os modelos
        """
        os.makedirs(directory, exist_ok=True)
        
        for name, result in self.trained_models.items():
            model_path = os.path.join(directory, f"{name.lower()}_model.pkl")
            joblib.dump(result['model'], model_path)
            print(f"Modelo {name} salvo em: {model_path}")
        
        # Salvar scaler e label encoder
        joblib.dump(self.scaler, os.path.join(directory, "scaler.pkl"))
        joblib.dump(self.label_encoder, os.path.join(directory, "label_encoder.pkl"))
        
    def generate_report(self) -> str:
        """
        Gera um relatório detalhado dos resultados.
        
        Returns:
            String com o relatório completo
        """
        if not self.trained_models:
            return "Nenhum modelo foi treinado ainda."
        
        report = "# Relatório de Avaliação dos Algoritmos de Machine Learning\n\n"
        report += "## Resumo Executivo\n\n"
        
        # Encontrar o melhor modelo
        best_model = max(self.trained_models.keys(), 
                        key=lambda x: self.trained_models[x]['accuracy'])
        best_accuracy = self.trained_models[best_model]['accuracy']
        
        report += f"O melhor modelo foi **{best_model}** com acurácia de **{best_accuracy:.4f}**.\n\n"
        
        report += "## Comparação Detalhada\n\n"
        report += "| Modelo | Acurácia | F1-Score | CV Média | CV Desvio |\n"
        report += "|--------|----------|----------|----------|----------|\n"
        
        for name, result in sorted(self.trained_models.items(), 
                                 key=lambda x: x[1]['accuracy'], reverse=True):
            report += f"| {name} | {result['accuracy']:.4f} | {result['f1_score']:.4f} | "
            report += f"{result['cv_mean']:.4f} | {result['cv_std']:.4f} |\n"
        
        report += "\n## Análise Individual dos Modelos\n\n"
        
        for name, result in self.trained_models.items():
            report += f"### {name}\n\n"
            report += f"**Acurácia:** {result['accuracy']:.4f}\n\n"
            report += f"**F1-Score:** {result['f1_score']:.4f}\n\n"
            report += f"**Cross-Validation:** {result['cv_mean']:.4f} ± {result['cv_std']:.4f}\n\n"
            report += "**Relatório de Classificação:**\n```\n"
            report += result['classification_report']
            report += "\n```\n\n"
        
        report += "## Conclusões\n\n"
        report += "Com base nos resultados obtidos, podemos concluir que:\n\n"
        report += f"1. O algoritmo **{best_model}** apresentou o melhor desempenho geral.\n"
        report += "2. Todos os modelos mostraram capacidade de generalização adequada.\n"
        report += "3. Os resultados de cross-validation indicam estabilidade dos modelos.\n"
        
        return report

def main():
    """Função principal para executar o pipeline de ML."""
    print("=== Pipeline de Machine Learning para Dados Educacionais ===\n")
    
    # Criar instância do pipeline
    ml_pipeline = EducationalMLPipeline()
    
    # Criar dataset de exemplo
    print("Criando dataset educacional de exemplo...")
    df = ml_pipeline.create_sample_educational_dataset()
    print(f"Dataset criado com {len(df)} amostras")
    print(f"Distribuição das classes: {df['performance'].value_counts().to_dict()}")
    
    # Pré-processar dados
    X, y = ml_pipeline.preprocess_data(df)
    
    # Treinar modelos
    results = ml_pipeline.train_models(X, y)
    
    # Avaliar modelos
    ml_pipeline.evaluate_models()
    
    # Gerar visualizações
    ml_pipeline.plot_results('ml_results.png')
    
    # Salvar modelos
    ml_pipeline.save_models('trained_models')
    
    # Gerar relatório
    report = ml_pipeline.generate_report()
    
    return ml_pipeline, report

if __name__ == "__main__":
    pipeline, report = main()

