"""
Unit tests for API functions.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from afm_tda_tools.api import run_acf, run_persistence, run_minmax, run_bottleneck


class TestAPI:
    """Тесты для API функций."""
    
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
    
    def test_run_acf(self, temp_csv_file):
        """Тест функции run_acf."""
        results = run_acf([temp_csv_file], width_line=0.1)
        
        assert isinstance(results, dict)
        assert temp_csv_file in results
        assert isinstance(results[temp_csv_file], pd.DataFrame)
        assert not results[temp_csv_file].empty
        assert 'ACF' in results[temp_csv_file].columns
        assert 'ix' in results[temp_csv_file].columns
        assert 'Axis' in results[temp_csv_file].columns
    
    def test_run_acf_multiple_files(self, temp_csv_file):
        """Тест функции run_acf с несколькими файлами."""
        # Создаем второй временный файл
        data2 = np.random.rand(8, 8) * 1e-7
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(data2)
            df.to_csv(f.name, index=False, header=False)
            temp_csv_file2 = f.name
        
        try:
            results = run_acf([temp_csv_file, temp_csv_file2], width_line=0.1)
            
            assert isinstance(results, dict)
            assert len(results) == 2
            assert temp_csv_file in results
            assert temp_csv_file2 in results
            assert all(isinstance(r, pd.DataFrame) for r in results.values())
            assert all(not r.empty for r in results.values())
        finally:
            os.unlink(temp_csv_file2)
    
    def test_run_persistence(self, temp_csv_file):
        """Тест функции run_persistence."""
        results = run_persistence([temp_csv_file], max_edge_length=10.0)
        
        assert isinstance(results, dict)
        assert temp_csv_file in results
        assert isinstance(results[temp_csv_file], tuple)
        assert len(results[temp_csv_file]) == 2
        
        diag, diag_df = results[temp_csv_file]
        assert isinstance(diag, list)
        assert isinstance(diag_df, pd.DataFrame)
        assert not diag_df.empty
        assert 'Start' in diag_df.columns
        assert 'End' in diag_df.columns
        assert 'Length' in diag_df.columns
        assert 'Homology group' in diag_df.columns
    
    def test_run_minmax(self, temp_csv_file):
        """Тест функции run_minmax."""
        results = run_minmax([temp_csv_file], matrix_size=3)
        
        assert isinstance(results, dict)
        assert temp_csv_file in results
        assert isinstance(results[temp_csv_file], tuple)
        assert len(results[temp_csv_file]) == 2
        
        agg_points, sub_mat_df = results[temp_csv_file]
        assert isinstance(agg_points, pd.DataFrame)
        assert isinstance(sub_mat_df, pd.DataFrame)
        assert not agg_points.empty
        assert 'r' in agg_points.columns
        assert 'c' in agg_points.columns
        assert 'X3' in agg_points.columns
        assert 'type' in agg_points.columns
    
    def test_run_bottleneck(self, temp_csv_file):
        """Тест функции run_bottleneck."""
        results = run_bottleneck([temp_csv_file], delta=0.01, order=1.0)
        
        assert isinstance(results, tuple)
        assert len(results) == 2
        
        bn_df, ws_df = results
        assert isinstance(bn_df, pd.DataFrame)
        assert isinstance(ws_df, pd.DataFrame)
        assert not bn_df.empty
        assert not ws_df.empty
    
    def test_api_with_different_parameters(self, temp_csv_file):
        """Тест API с разными параметрами."""
        # Тест автокорреляции с разными width_line
        for width_line in [0.01, 0.05, 0.1]:
            results = run_acf([temp_csv_file], width_line=width_line)
            assert isinstance(results, dict)
            assert temp_csv_file in results
        
        # Тест персистентной гомологии с разными max_edge_length
        for max_edge_length in [5.0, 10.0, 20.0]:
            results = run_persistence([temp_csv_file], max_edge_length=max_edge_length)
            assert isinstance(results, dict)
            assert temp_csv_file in results
        
        # Тест min-max с разными размерами матриц
        for matrix_size in [2, 3]:
            results = run_minmax([temp_csv_file], matrix_size=matrix_size)
            assert isinstance(results, dict)
            assert temp_csv_file in results
        
        # Тест bottleneck с разными параметрами
        for delta in [0.005, 0.01, 0.02]:
            for order in [1.0, 2.0]:
                results = run_bottleneck([temp_csv_file], delta=delta, order=order)
                assert isinstance(results, tuple)
                assert len(results) == 2


class TestAPIWithRealData:
    """Тесты API с реальными данными."""
    
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
    
    def test_run_acf_with_real_data(self, real_data_path):
        """Тест run_acf с реальными данными."""
        results = run_acf([real_data_path], width_line=0.1)
        
        assert isinstance(results, dict)
        assert real_data_path in results
        assert isinstance(results[real_data_path], pd.DataFrame)
        assert not results[real_data_path].empty
        assert 'ACF' in results[real_data_path].columns
        assert 'ix' in results[real_data_path].columns
        assert 'Axis' in results[real_data_path].columns
    
    def test_run_persistence_with_real_data(self, real_data_path):
        """Тест run_persistence с реальными данными."""
        results = run_persistence([real_data_path], max_edge_length=50.0)
        
        assert isinstance(results, dict)
        assert real_data_path in results
        assert isinstance(results[real_data_path], tuple)
        
        diag, diag_df = results[real_data_path]
        assert isinstance(diag, list)
        assert isinstance(diag_df, pd.DataFrame)
        assert not diag_df.empty
        assert 'Start' in diag_df.columns
        assert 'End' in diag_df.columns
        assert 'Length' in diag_df.columns
        assert 'Homology group' in diag_df.columns
    
    def test_run_minmax_with_real_data(self, real_data_path):
        """Тест run_minmax с реальными данными."""
        results = run_minmax([real_data_path], matrix_size=3)
        
        assert isinstance(results, dict)
        assert real_data_path in results
        assert isinstance(results[real_data_path], tuple)
        
        agg_points, sub_mat_df = results[real_data_path]
        assert isinstance(agg_points, pd.DataFrame)
        assert isinstance(sub_mat_df, pd.DataFrame)
        assert not agg_points.empty
        assert 'r' in agg_points.columns
        assert 'c' in agg_points.columns
        assert 'X3' in agg_points.columns
        assert 'type' in agg_points.columns
    
    def test_run_bottleneck_with_real_data(self, real_data_path):
        """Тест run_bottleneck с реальными данными."""
        results = run_bottleneck([real_data_path], delta=0.01, order=1.0)
        
        assert isinstance(results, tuple)
        assert len(results) == 2
        
        bn_df, ws_df = results
        assert isinstance(bn_df, pd.DataFrame)
        assert isinstance(ws_df, pd.DataFrame)
        assert not bn_df.empty
        assert not ws_df.empty 