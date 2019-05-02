import pandas as pd
import numpy as np

from scattertext.Scalers import stretch_neg1_to_1


class CategoryProjectionBase(object):
    def __init__(self, category_corpus, category_counts, projection, x_dim=0, y_dim=1, **kwargs):
        self.category_corpus = category_corpus
        self.category_counts = category_counts
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.projection = projection

    def project_with_alternative_dimensions(self, x_dim, y_dim):
        return CategoryProjection(self.category_corpus, self.category_counts, self.projection, x_dim, y_dim)

    def project_with_alternate_axes(self, x_axis=None, y_axis=None):
        # !!! Need to fix
        if x_axis is None:
           x_axis = self._get_x_axis()
        if y_axis is None:
           y_axis = self._get_y_axis()
        return CategoryProjectionAlternateAxes(self.category_corpus,
                                               self.category_counts,
                                               self.projection,
                                               self.get_category_embeddings(),
                                               self.x_dim,
                                               self.y_dim,
                                               x_axis=x_axis,
                                               y_axis=y_axis)

    def get_pandas_projection(self):
        '''

        :param x_dim: int
        :param y_dim: int
        :return: pd.DataFrame
        '''
        return pd.DataFrame({'term': self.category_corpus.get_metadata(),
                             'x': self._get_x_axis(),
                             'y': self._get_y_axis()}).set_index('term')

    def _get_x_axis(self):
        return self.projection.T[self.x_dim]

    def _get_y_axis(self):
        return self.projection.T[self.y_dim]

    def get_axes_labels(self, num_terms=5):
        df = self.get_term_projection()
        return {'right': list(df.sort_values(by='x', ascending=False).index[:num_terms]),
                'left': list(df.sort_values(by='x', ascending=True).index[:num_terms]),
                'top': list(df.sort_values(by='y', ascending=False).index[:num_terms]),
                'bottom': list(df.sort_values(by='y', ascending=True).index[:num_terms])}

    def get_nearest_terms(self, num_terms=5):
        df = self.get_term_projection().apply(stretch_neg1_to_1)
        return {
            'top_right': ((df.x - 1) ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'top': (df.x ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'top_left': ((df.x + 1) ** 2 + (df.y - 1) ** 2).sort_values().index[:num_terms].values,
            'right': ((df.x - 1) ** 2 + df.y ** 2).sort_values().index[:num_terms].values,
            'left': ((df.x + 1) ** 2 + df.y ** 2).sort_values().index[:num_terms].values,
            'bottom_right': ((df.x - 1) ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
            'bottom': (df.x ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
            'bottom_left': ((df.x + 1) ** 2 + (df.y + 1) ** 2).sort_values().index[:num_terms].values,
        }

    def get_term_projection(self):
        dim_term = np.matrix(self.category_counts.values) * self._get_x_y_projection()
        df = pd.DataFrame(dim_term, index=self.category_corpus.get_terms(), columns=['x', 'y'])
        return df

    def _get_x_y_projection(self):
        return np.array([self._get_x_axis(), self._get_y_axis()]).T

    def get_category_embeddings(self):
        raise NotImplementedError()


class CategoryProjection(CategoryProjectionBase):
    def __init__(self, category_corpus, category_counts, projection, x_dim=0, y_dim=1):
        CategoryProjectionBase.__init__(self, category_corpus, category_counts, projection, x_dim, y_dim)

    def get_category_embeddings(self):
        return self.category_counts.values


class CategoryProjectionWithDoc2Vec(CategoryProjectionBase):
    def __init__(self, category_corpus, category_counts, projection, x_dim=0, y_dim=1, doc2vec_model=None):
        self.doc2vec_model = doc2vec_model
        CategoryProjectionBase.__init__(self, category_corpus, category_counts, projection, x_dim, y_dim)

    def project_with_alternative_dimensions(self, x_dim, y_dim):
        return CategoryProjectionWithDoc2Vec(self.category_corpus, self.category_counts, self.projection,
                                             x_dim, y_dim, doc2vec_model=self.doc2vec_model)

    def get_category_embeddings(self):
        return self.doc2vec_model.project()

#!!! Need to fix
class CategoryProjectionAlternateAxes(CategoryProjectionBase):
    def __init__(self, category_corpus, category_counts, projection, category_embeddings, x_dim=0, y_dim=1, x_axis=None,
                 y_axis=None):
        CategoryProjectionBase.__init__(self, category_corpus, category_counts, projection, x_dim=0, y_dim=1)
        self.x_axis_ = x_axis
        self.y_axis_ = y_axis
        self.category_embeddings_ = category_embeddings

    def get_category_embeddings(self):
        return self.category_embeddings_

    def _get_x_axis(self):
        return self.x_axis_

    def _get_y_axis(self):
        return self.y_axis_



