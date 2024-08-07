import tensorflow as tf

class Prediction:
    def __init__(self, rows, features, model):
        self._rows = rows
        self._model = model
        self._features = features
        
    def compute_prediction(self, feature_name):
        if self._model is not None:
            return self.compute_supervised_prediction(feature_name)
        else:
            return self.compute_unsupervised_ranking(feature_name)

    def compute_supervised_prediction(self, feature_name):
        prediction = []
        indexes = []
        for column_features in self._features:
            pred = [] 
            if len(column_features) > 0:
                pred = self._model.predict(tf.convert_to_tensor(column_features))
            prediction.append(pred)
            indexes.append(0)
        
        for row in self._rows:
            cells = row.get_cells()
            for cell in cells:
                candidates = cell.candidates()
                for candidate in candidates:
                    index = indexes[cell._id_col]
                    indexes[cell._id_col] += 1
                    feature = round(float(prediction[cell._id_col][index][1]), 3)
                    candidate[feature_name] = feature
                
                candidates.sort(key=lambda x: x[feature_name], reverse=True)  
                
    def compute_unsupervised_ranking(self, feature_name):
        feature_indices = [
            'ed_score', 'jaccard_score', 'jaccardNgram_score', 
            'p_subj_ne', 'p_subj_lit_datatype', 'p_subj_lit_all_datatype', 
            'p_subj_lit_row', 'p_obj_ne', 'cta_t1', 'cta_t2', 'cta_t3', 'cta_t4', 
            'cta_t5', 'cpa_t1', 'cpa_t2', 'cpa_t3', 'cpa_t4', 'cpa_t5'
        ]

        subset_features = [
            [feature[i] for i, name in enumerate(self._features[0]) if name in feature_indices]
            for feature in self._features
        ]
        weights = [1 / len(subset_features[0])] * len(subset_features[0])  # Equal weights to normalize

        rankings = []
        for candidate in subset_features:
            score = sum([w * x for w, x in zip(weights, candidate)])
            rankings.append(score)
        
        indexes = [0] * len(self._features)

        for row in self._rows:
            cells = row.get_cells()
            for cell in cells:
                candidates = cell.candidates()
                for candidate in candidates:
                    index = indexes[cell._id_col]
                    indexes[cell._id_col] += 1
                    feature = round(rankings[index], 3)
                    candidate[feature_name] = feature
                
                candidates.sort(key=lambda x: x[feature_name], reverse=True)

