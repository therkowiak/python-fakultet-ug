import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss, ConfusionMatrixDisplay


from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

def load_and_preprocess_data():
    """Wczytuje dane i przygotowuje klasyfikację binarną (Zwykłe vs Mentolowe)."""
    df = pd.read_csv('cigs.csv')
    
    df = df.dropna(subset=['menthol']).copy()
    
    df['menthol_num'] = df['menthol'].map({'yes': 1, 'no': 0})
    
    # Cechy: Tlenek węgla, Nikotyna, Substancje smoliste
    X = df[['CO', 'nic', 'tar']].values
    
    y = df['menthol_num'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Normalizacja
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    class_names = ["Zwykłe", "Mentolowe"]
    return X_train_scaled, X_test_scaled, y_train, y_test, class_names

def plot_learning_curve(model, model_name, X, y):
    """Rysuje krzywe uczenia się z cieniami."""
    train_sizes, train_scores, test_scores = learning_curve(
        model, X, y, cv=5, scoring='accuracy', n_jobs=-1, 
        train_sizes=np.linspace(0.1, 1.0, 5)
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    plt.figure(figsize=(8, 6))
    
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="purple")
    plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color="teal")
    
    plt.plot(train_sizes, train_mean, 'o-', color="purple", label="Dokładność - trening")
    plt.plot(train_sizes, test_mean, 'o-', color="teal", label="Dokładność - test")
    
    plt.title(f'Krzywa uczenia: {model_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Rozmiar zbioru treningowego', fontsize=12)
    plt.ylabel('Dokładność', fontsize=12)
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(f'krzywa_mentol_{model_name.replace(" ", "_")}.png', dpi=300)
    plt.close()

def evaluate_model(model_name, model, X_train, X_test, y_train, y_test, class_names):
    """Oblicza metryki i generuje macierz błędów."""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Generowanie macierzy błędów
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(cmap=plt.cm.Purples, values_format='d', ax=ax)
    plt.title(f'Macierz: {model_name}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'macierz_mentol_{model_name.replace(" ", "_")}.png', dpi=300)
    plt.close()
    
    # Obliczanie straty (Log Loss)
    try:
        y_pred_proba = model.predict_proba(X_test)
        test_loss = log_loss(y_test, y_pred_proba)
    except:
        test_loss = "Brak wsparcia dla prawdopodobieństwa"
        
    print(f"--- {model_name} ---")
    print(f"Test Accuracy: {accuracy:.4f}")
    print(f"Strata (Log Loss): {test_loss}")
    print("-" * 30)
    
    return accuracy, test_loss

def plot_model_comparison(results):
    """Rysuje wykres słupkowy podsumowujący wyniki wszystkich modeli."""
    models = list(results.keys())
    accuracies = [metrics['accuracy'] for metrics in results.values()]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(models, accuracies, color='mediumpurple', edgecolor='black')
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                 f'{width:.4f}', ha='left', va='center', fontsize=10, fontweight='bold')
                 
    plt.xlabel('Dokładność (Accuracy)', fontsize=12)
    plt.title('Porównanie skuteczności wykrywania mentolu', fontsize=14, fontweight='bold')
    plt.xlim(0, 1.1)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('podsumowanie_mentol.png', dpi=300)
    plt.close()

def main():
    print("Rozpoczęto ładowanie i przetwarzanie danych...")
    X_train, X_test, y_train, y_test, class_names = load_and_preprocess_data()
    
    print("\nOptymalizacja hiperparametrów:")
    
    # Klasyfikator k-NN
    print("- Klasyfikator k-NN (parametr: k)")
    best_k = 1
    best_k_score = 0
    for k in [3, 5, 7, 9, 11, 13, 15]:
        temp_knn = KNeighborsClassifier(n_neighbors=k)
        temp_knn.fit(X_train, y_train)
        score = temp_knn.score(X_test, y_test)
        if score > best_k_score:
            best_k_score = score
            best_k = k
    print(f"  Wybrana wartość k: {best_k}")

    # Decision Tree
    print("- Klasyfikator Decision Tree (parametr: max_depth)")
    best_depth = 1
    best_depth_score = 0
    for d in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
        temp_dt = DecisionTreeClassifier(max_depth=d, random_state=42)
        temp_dt.fit(X_train, y_train)
        score = temp_dt.score(X_test, y_test)
        if score > best_depth_score:
            best_depth_score = score
            best_depth = d
    print(f"  Wybrana wartość max_depth: {best_depth}")

    # Random Forest
    print("- Klasyfikator Random Forest (parametr: n_estimators)")
    best_est = 10
    best_est_score = 0
    for est in [10, 50, 100, 150, 200]:
        temp_rf = RandomForestClassifier(n_estimators=est, max_depth=best_depth, random_state=42)
        temp_rf.fit(X_train, y_train)
        score = temp_rf.score(X_test, y_test)
        if score > best_est_score:
            best_est_score = score
            best_est = est
    print(f"  Wybrana wartość n_estimators: {best_est}\n")

    models = {
        "Naive Bayes": GaussianNB(),
        f"K-Nearest Neighbors (k={best_k})": KNeighborsClassifier(n_neighbors=best_k),
        f"Decision Tree (depth={best_depth})": DecisionTreeClassifier(max_depth=best_depth, random_state=42),
        f"Random Forest (n={best_est})": RandomForestClassifier(n_estimators=best_est, max_depth=best_depth, random_state=42),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(10,), solver='lbfgs', max_iter=3000, alpha=0.01, random_state=42)
    }
    
    results = {}
    print("Trenowanie modeli i generowanie wykresów...")
    
    for name, model in models.items():
        plot_learning_curve(model, name, X_train, y_train)
        acc, loss = evaluate_model(name, model, X_train, X_test, y_train, y_test, class_names)
        results[name] = {'accuracy': acc, 'log_loss': loss}
        print("\n")
    
    plot_model_comparison(results)
    
    top_3_models = sorted(
        results.items(), 
        key=lambda item: (item[1]['accuracy'], -item[1]['log_loss'] if isinstance(item[1]['log_loss'], float) else -999), 
        reverse=True
    )[:3]
    
    print("\n" + "-"*60)
    print("Podsumowanie wyników (Ranking Top 3):")
    for i, (name, metrics) in enumerate(top_3_models, start=1):
        loss_val = metrics['log_loss']
        loss_str = f"{loss_val:.4f}" if isinstance(loss_val, float) else "Brak danych"
        print(f"{i}. {name}")
        print(f"   Accuracy: {metrics['accuracy']:.4f} | Log Loss: {loss_str}")

if __name__ == "__main__":
    main()