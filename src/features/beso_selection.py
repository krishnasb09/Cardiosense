import logging
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class BESOFeatureSelector:
    """
    Implementation of Bald Eagle Search Optimization (BESO) for feature selection.
    This version uses binary encoding for feature subsets.
    """

    def __init__(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        feature_names: List[str],
        pop_size: int = 20, 
        max_iter: int = 50,
        random_state: int = 42
    ):
        self.X = X
        self.y = y.ravel()
        self.feature_names = feature_names
        self.n_features = X.shape[1]
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Hyperparameters for BES
        self.alpha = 1.5 # Parameter for selection phase
        self.R = 0.5     # Parameter for search phase
        self.c1 = 1.5    # Parameter for swoop phase
        self.c2 = 2.0    # Parameter for swoop phase

    def _fitness(self, position: np.ndarray) -> float:
        """
        Calculate fitness of a feature subset using ROC-AUC of LogisticRegression.
        Binary encoding: features with position > 0.5 are selected.
        """
        selected_indices = np.where(position > 0.5)[0]
        
        if len(selected_indices) == 0:
            return 0.0
        
        # Subselect features
        X_subset = self.X[:, selected_indices]
        
        # Use cross-validation to get ROC-AUC
        model = LogisticRegression(max_iter=1000, random_state=self.random_state)
        try:
            # We use 3-fold CV for speed during optimization
            scores = cross_val_score(model, X_subset, self.y, cv=3, scoring='roc_auc')
            return np.mean(scores)
        except Exception as e:
            logger.debug(f"Fitness calculation failed: {e}")
            return 0.0

    def select(self) -> List[str]:
        """
        Run BESO and return the best feature subset.
        """
        logger.info(f"Starting BESO with pop_size={self.pop_size}, max_iter={self.max_iter}")
        
        # Initialize population (continuous between 0 and 1)
        pop = np.random.rand(self.pop_size, self.n_features)
        fitness = np.array([self._fitness(ind) for ind in pop])
        
        # Find best global
        best_idx = np.argmax(fitness)
        best_pos = pop[best_idx].copy()
        best_score = fitness[best_idx]
        
        for i in range(self.max_iter):
            # 1. Selection Phase
            logger.debug(f"Iteration {i+1}: Selection Phase")
            mean_pos = np.mean(pop, axis=0)
            for j in range(self.pop_size):
                # Update position towards best and mean
                pop[j] = best_pos + self.alpha * np.random.rand() * (mean_pos - pop[j])
                pop[j] = np.clip(pop[j], 0, 1)
            
            # 2. Search Phase
            logger.debug(f"Iteration {i+1}: Search Phase")
            for j in range(self.pop_size):
                # Spiral search pattern
                idx = np.random.randint(0, self.pop_size)
                pop[j] = pop[j] + np.random.randn(self.n_features) * (pop[j] - pop[idx])
                pop[j] = np.clip(pop[j], 0, 1)
                
            # 3. Swoop Phase
            logger.debug(f"Iteration {i+1}: Swoop Phase")
            for j in range(self.pop_size):
                # Move towards best
                pop[j] = np.random.rand() * best_pos + self.c1 * np.random.rand() * (pop[j] - mean_pos) + \
                         self.c2 * np.random.rand() * (pop[j] - best_pos)
                pop[j] = np.clip(pop[j], 0, 1)
                
            # Update fitness and best
            fitness = np.array([self._fitness(ind) for ind in pop])
            current_best_idx = np.argmax(fitness)
            if fitness[current_best_idx] > best_score:
                best_score = fitness[current_best_idx]
                best_pos = pop[current_best_idx].copy()
                logger.debug(f"New best score at iteration {i+1}: {best_score:.4f}")

            if (i + 1) % 5 == 0:
                logger.info(f"Iteration {i+1}/{self.max_iter}: Best Score = {best_score:.4f}")

        # Final selection
        selected_indices = np.where(best_pos > 0.5)[0]
        selected_features = [self.feature_names[idx] for idx in selected_indices]
        
        logger.info(f"BESO completed. Selected {len(selected_features)} features. Final ROC-AUC: {best_score:.4f}")
        return selected_features

def select_features_beso(
    X: np.ndarray, 
    y: np.ndarray, 
    feature_names: List[str],
    pop_size: int = 20,
    max_iter: int = 50,
    random_state: int = 42
) -> List[str]:
    """
    Orchestrator for BESO feature selection.
    """
    selector = BESOFeatureSelector(
        X, y, feature_names, 
        pop_size=pop_size, 
        max_iter=max_iter, 
        random_state=random_state
    )
    return selector.select()
