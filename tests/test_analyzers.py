"""
Unit tests for AFM TDA analyzers.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from afm_tda_tools.analyzers.autocorrelation import AutocorrelationAnalyzer
from afm_tda_tools.analyzers.persistence import PersistenceAnalyzer
from afm_tda_tools.analyzers.min_max import MinMaxAnalyzer
from afm_tda_tools.analyzers.bottleneck import BottleneckAnalyzer


class TestAutocorrelationAnalyzer:
    """Тесты для AutocorrelationAnalyzer."""
    
    @pytest.fixture
    def sample_data(self):
        """Создает тестовые данные."""
        # Создаем простую матрицу 10x10 для тестирования
        data = np.random.rand(10, 10) * 1e-7
        return data
    
    @pytest.fixture
    def temp_csv_file(self, sample_data):
        """Создает временный CSV файл с тестовыми данными."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(sample_data)
            df.to_csv(f.name, index=False, header=False)
            yield f.name
        os.unlink(f.name)
    
    def test_autocorrelation_analyzer_initialization(self):
        """Тест инициализации анализатора."""
        analyzer = AutocorrelationAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'compute')
    
    def test_autocorrelation_computation(self, temp_csv_file):
        """Тест вычисления автокорреляции."""
        analyzer = AutocorrelationAnalyzer()
        results = analyzer.compute(temp_csv_file, width_line=0.1)
        
        assert isinstance(results, pd.DataFrame)
        assert not results.empty
        assert 'ACF' in results.columns
        assert 'ix' in results.columns
        assert 'Axis' in results.columns
    
    def test_autocorrelation_with_different_width_line(self, temp_csv_file):
        """Тест с разными значениями width_line."""
        analyzer = AutocorrelationAnalyzer()
        
        # Тест с разными значениями
        for width_line in [0.01, 0.05, 0.1]:
            results = analyzer.compute(temp_csv_file, width_line=width_line)
            assert isinstance(results, pd.DataFrame)
            assert not results.empty


class TestPersistenceAnalyzer:
    """Тесты для PersistenceAnalyzer."""
    
    @pytest.fixture
    def sample_data(self):
        """Создает тестовые данные."""
        # Создаем простую матрицу 5x5 для быстрого тестирования
        data = np.random.rand(5, 5) * 1e-7
        return data
    
    @pytest.fixture
    def temp_csv_file(self, sample_data):
        """Создает временный CSV файл с тестовыми данными."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(sample_data)
            df.to_csv(f.name, index=False, header=False)
            yield f.name
        os.unlink(f.name)
    
    def test_persistence_analyzer_initialization(self):
        """Тест инициализации анализатора."""
        analyzer = PersistenceAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'compute')
    
    def test_persistence_computation(self, temp_csv_file):
        """Тест вычисления персистентной гомологии."""
        analyzer = PersistenceAnalyzer()
        diag, diag_df = analyzer.compute(temp_csv_file, max_edge_length=10.0)
        
        assert isinstance(diag, list)
        assert isinstance(diag_df, pd.DataFrame)
        assert not diag_df.empty
        assert 'Start' in diag_df.columns
        assert 'End' in diag_df.columns
        assert 'Length' in diag_df.columns
        assert 'Homology group' in diag_df.columns
    
    def test_persistence_with_different_max_edge_length(self, temp_csv_file):
        """Тест с разными значениями max_edge_length."""
        analyzer = PersistenceAnalyzer()
        
        for max_edge_length in [5.0, 10.0, 20.0]:
            diag, diag_df = analyzer.compute(temp_csv_file, max_edge_length=max_edge_length)
            assert isinstance(diag, list)
            assert isinstance(diag_df, pd.DataFrame)


class TestMinMaxAnalyzer:
    """Тесты для MinMaxAnalyzer."""
    
    @pytest.fixture
    def sample_data(self):
        """Создает тестовые данные."""
        # Создаем простую матрицу 6x6 для тестирования (делится на 3)
        data = np.random.rand(6, 6) * 1e-7
        return data
    
    @pytest.fixture
    def temp_csv_file(self, sample_data):
        """Создает временный CSV файл с тестовыми данными."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(sample_data)
            df.to_csv(f.name, index=False, header=False)
            yield f.name
        os.unlink(f.name)
    
    def test_minmax_analyzer_initialization(self):
        """Тест инициализации анализатора."""
        analyzer = MinMaxAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'compute')
    
    def test_minmax_computation(self, temp_csv_file):
        """Тест вычисления min-max анализа."""
        analyzer = MinMaxAnalyzer()
        agg_points, sub_mat_df = analyzer.compute(temp_csv_file, matrix_size=3)
        
        assert isinstance(agg_points, pd.DataFrame)
        assert isinstance(sub_mat_df, pd.DataFrame)
        assert not agg_points.empty
        assert 'r' in agg_points.columns
        assert 'c' in agg_points.columns
        assert 'X3' in agg_points.columns
        assert 'type' in agg_points.columns
    
    def test_minmax_with_different_matrix_sizes(self, temp_csv_file):
        """Тест с разными размерами матриц."""
        analyzer = MinMaxAnalyzer()
        
        # Тестируем с матрицей 6x6, которая делится на 2 и 3
        for matrix_size in [2, 3]:
            agg_points, sub_mat_df = analyzer.compute(temp_csv_file, matrix_size=matrix_size)
            assert isinstance(agg_points, pd.DataFrame)
            assert isinstance(sub_mat_df, pd.DataFrame)


class TestBottleneckAnalyzer:
    """Тесты для BottleneckAnalyzer."""
    
    @pytest.fixture
    def sample_data(self):
        """Создает тестовые данные."""
        # Создаем простую матрицу 5x5 для тестирования
        data = np.random.rand(5, 5) * 1e-7
        return data
    
    @pytest.fixture
    def temp_csv_file(self, sample_data):
        """Создает временный CSV файл с тестовыми данными."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(sample_data)
            df.to_csv(f.name, index=False, header=False)
            yield f.name
        os.unlink(f.name)
    
    def test_bottleneck_analyzer_initialization(self):
        """Тест инициализации анализатора."""
        analyzer = BottleneckAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'compute')
    
    def test_bottleneck_computation(self, temp_csv_file):
        """Тест вычисления bottleneck расстояния."""
        analyzer = BottleneckAnalyzer()
        bn_df, ws_df = analyzer.compute([temp_csv_file], delta=0.01, order=1.0)
        
        assert isinstance(bn_df, pd.DataFrame)
        assert isinstance(ws_df, pd.DataFrame)
        assert not bn_df.empty
        assert not ws_df.empty
    
    def test_bottleneck_with_different_parameters(self, temp_csv_file):
        """Тест с разными параметрами."""
        analyzer = BottleneckAnalyzer()
        
        for delta in [0.005, 0.01, 0.02]:
            for order in [1.0, 2.0]:
                bn_df, ws_df = analyzer.compute([temp_csv_file], delta=delta, order=order)
                assert isinstance(bn_df, pd.DataFrame)
                assert isinstance(ws_df, pd.DataFrame)


class TestWithRealData:
    """Тесты с реальными данными из test_files."""
    
    @pytest.fixture
    def real_data_path(self):
        """Путь к реальным данным."""
        data_dir = Path("test_files")
        if data_dir.exists():
            # Берем первый файл для тестирования
            files = list(data_dir.glob("*.txt"))
            if files:
                return str(files[0])
        pytest.skip("Real data not available")
    
    def test_autocorrelation_with_real_data(self, real_data_path):
        """Тест автокорреляции с реальными данными."""
        analyzer = AutocorrelationAnalyzer()
        results = analyzer.compute(real_data_path, width_line=0.1)
        
        assert isinstance(results, pd.DataFrame)
        assert not results.empty
        assert 'ACF' in results.columns
        assert 'ix' in results.columns
        assert 'Axis' in results.columns
    
    def test_persistence_with_real_data(self, real_data_path):
        """Тест персистентной гомологии с реальными данными."""
        analyzer = PersistenceAnalyzer()
        diag, diag_df = analyzer.compute(real_data_path, max_edge_length=50.0)
        
        assert isinstance(diag, list)
        assert isinstance(diag_df, pd.DataFrame)
        assert not diag_df.empty
        assert 'Start' in diag_df.columns
        assert 'End' in diag_df.columns
        assert 'Length' in diag_df.columns
        assert 'Homology group' in diag_df.columns
    
    def test_minmax_with_real_data(self, real_data_path):
        """Тест min-max анализа с реальными данными."""
        analyzer = MinMaxAnalyzer()
        agg_points, sub_mat_df = analyzer.compute(real_data_path, matrix_size=3)
        
        assert isinstance(agg_points, pd.DataFrame)
        assert isinstance(sub_mat_df, pd.DataFrame)
        assert not agg_points.empty
        assert 'r' in agg_points.columns
        assert 'c' in agg_points.columns
        assert 'X3' in agg_points.columns
        assert 'type' in agg_points.columns
    
    def test_bottleneck_with_real_data(self, real_data_path):
        """Тест bottleneck расстояния с реальными данными."""
        analyzer = BottleneckAnalyzer()
        bn_df, ws_df = analyzer.compute([real_data_path], delta=0.01, order=1.0)
        
        assert isinstance(bn_df, pd.DataFrame)
        assert isinstance(ws_df, pd.DataFrame)
        assert not bn_df.empty
        assert not ws_df.empty 