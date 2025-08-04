"""
Unit tests for AnalysisPipeline.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import shutil
from pathlib import Path

from afm_tda_tools.pipeline import AnalysisPipeline


class TestAnalysisPipeline:
    """Тесты для AnalysisPipeline."""
    
    @pytest.fixture
    def sample_data(self):
        """Создает тестовые данные."""
        # Создаем простую матрицу 10x10 для тестирования
        data = np.random.rand(10, 10) * 1e-7
        return data
    
    @pytest.fixture
    def temp_data_dir(self, sample_data):
        """Создает временную директорию с тестовыми данными."""
        temp_dir = tempfile.mkdtemp()
        
        # Создаем несколько тестовых файлов
        for i in range(3):
            data = np.random.rand(8, 8) * 1e-7
            file_path = os.path.join(temp_dir, f"test_data_{i}.txt")
            
            # Создаем файл в формате AFM
            with open(file_path, 'w') as f:
                f.write("# Канал: Height (2)\n")
                f.write("# Ширина: 5.02 µm\n")
                f.write("# Высота: 5.02 µm\n")
                f.write("# Единицы измерения: m\n")
                
                for row in data:
                    f.write('\t'.join([f"{val:.6e}" for val in row]) + '\n')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Создает временную директорию для результатов."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_pipeline_initialization(self):
        """Тест инициализации pipeline."""
        pipeline = AnalysisPipeline(
            data_path="/tmp/test",
            save_path="/tmp/output"
        )
        
        assert pipeline is not None
        assert hasattr(pipeline, 'run')
        assert pipeline.data_path == "/tmp/test"
        assert pipeline.save_path == "/tmp/output"
    
    def test_pipeline_with_default_parameters(self, temp_data_dir, temp_output_dir):
        """Тест pipeline с параметрами по умолчанию."""
        pipeline = AnalysisPipeline(
            data_path=temp_data_dir,
            save_path=temp_output_dir
        )
        
        # Запускаем pipeline
        pipeline.run()
        
        # Проверяем, что создались файлы результатов
        output_files = list(Path(temp_output_dir).glob("*"))
        assert len(output_files) > 0
    
    def test_pipeline_with_custom_parameters(self, temp_data_dir, temp_output_dir):
        """Тест pipeline с пользовательскими параметрами."""
        pipeline = AnalysisPipeline(
            data_path=temp_data_dir,
            save_path=temp_output_dir,
            width_line=0.05,
            max_edge_length=50.0,
            matrix_size=2,
            delta=0.005,
            order=2.0,
            multiply_const=1e8
        )
        
        # Запускаем pipeline
        pipeline.run()
        
        # Проверяем, что создались файлы результатов
        output_files = list(Path(temp_output_dir).glob("*"))
        assert len(output_files) > 0
    
    def test_pipeline_exclude_patterns(self, temp_data_dir, temp_output_dir):
        """Тест исключения файлов по паттернам."""
        # Создаем файл, который должен быть исключен
        exclude_file = os.path.join(temp_data_dir, "excluded_file.txt")
        with open(exclude_file, 'w') as f:
            f.write("test data")
        
        pipeline = AnalysisPipeline(
            data_path=temp_data_dir,
            save_path=temp_output_dir,
            exclude_patterns=["excluded_file.txt"]
        )
        
        # Запускаем pipeline
        pipeline.run()
        
        # Проверяем, что создались файлы результатов
        output_files = list(Path(temp_output_dir).glob("*"))
        assert len(output_files) > 0
    
    def test_pipeline_data_validation(self):
        """Тест валидации данных."""
        # Тест с несуществующей директорией
        with pytest.raises(Exception):
            pipeline = AnalysisPipeline(
                data_path="/nonexistent/path",
                save_path="/tmp/output"
            )
            pipeline.run()
    
    def test_pipeline_output_structure(self, temp_data_dir, temp_output_dir):
        """Тест структуры выходных данных."""
        pipeline = AnalysisPipeline(
            data_path=temp_data_dir,
            save_path=temp_output_dir
        )
        
        # Запускаем pipeline
        pipeline.run()
        
        # Проверяем структуру выходных файлов
        output_files = list(Path(temp_output_dir).glob("*"))
        
        # Должны быть созданы файлы результатов
        assert len(output_files) > 0
        
        # Проверяем наличие файлов результатов (любого типа)
        result_files = [f for f in output_files if f.is_file()]
        assert len(result_files) > 0


class TestPipelineWithRealData:
    """Тесты pipeline с реальными данными."""
    
    @pytest.fixture
    def real_data_dir(self):
        """Путь к реальным данным."""
        data_dir = Path("test_files")
        if data_dir.exists():
            return str(data_dir)
        pytest.skip("Real data not available")
    
    @pytest.fixture
    def temp_output_dir(self):
        """Создает временную директорию для результатов."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_pipeline_with_real_data(self, real_data_dir, temp_output_dir):
        """Тест pipeline с реальными данными."""
        pipeline = AnalysisPipeline(
            data_path=real_data_dir,
            save_path=temp_output_dir,
            width_line=0.0196,
            max_edge_length=100.0,
            matrix_size=3,
            delta=0.01,
            order=1.0,
            multiply_const=1e9
        )
        
        # Запускаем pipeline
        pipeline.run()
        
        # Проверяем, что создались файлы результатов
        output_files = list(Path(temp_output_dir).glob("*"))
        assert len(output_files) > 0
        
        # Проверяем наличие файлов результатов (любого типа)
        result_files = [f for f in output_files if f.is_file()]
        assert len(result_files) > 0
    
    def test_pipeline_with_real_data_subset(self, real_data_dir, temp_output_dir):
        """Тест pipeline с подмножеством реальных данных."""
        # Создаем временную директорию с несколькими файлами
        temp_data_dir = tempfile.mkdtemp()
        try:
            # Копируем только первые 2 файла
            data_files = list(Path(real_data_dir).glob("*.txt"))[:2]
            for file_path in data_files:
                shutil.copy2(file_path, temp_data_dir)
            
            pipeline = AnalysisPipeline(
                data_path=temp_data_dir,
                save_path=temp_output_dir,
                width_line=0.1,
                max_edge_length=30.0,
                matrix_size=3,
                delta=0.01,
                order=1.0,
                multiply_const=1e9
            )
            
            # Запускаем pipeline
            pipeline.run()
            
            # Проверяем, что создались файлы результатов
            output_files = list(Path(temp_output_dir).glob("*"))
            assert len(output_files) > 0
            
        finally:
            shutil.rmtree(temp_data_dir)


class TestPipelineErrorHandling:
    """Тесты обработки ошибок в pipeline."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Создает временную директорию для результатов."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_pipeline_invalid_data_path(self, temp_output_dir):
        """Тест с неверным путем к данным."""
        with pytest.raises((FileNotFoundError, ValueError, OSError)):
            pipeline = AnalysisPipeline(
                data_path="/nonexistent/path",
                save_path=temp_output_dir
            )
            pipeline.run()
    
    def test_pipeline_invalid_save_path(self, temp_data_dir):
        """Тест с неверным путем сохранения."""
        with pytest.raises((FileNotFoundError, ValueError, OSError)):
            pipeline = AnalysisPipeline(
                data_path=temp_data_dir,
                save_path="/nonexistent/output"
            )
            pipeline.run()
    
    def test_pipeline_empty_data_directory(self, temp_output_dir):
        """Тест с пустой директорией данных."""
        empty_dir = tempfile.mkdtemp()
        try:
            pipeline = AnalysisPipeline(
                data_path=empty_dir,
                save_path=temp_output_dir
            )
            
            # Pipeline должен завершиться без ошибок, но без результатов
            pipeline.run()
            
            # Проверяем, что выходная директория пуста
            output_files = list(Path(temp_output_dir).glob("*"))
            assert len(output_files) == 0
            
        finally:
            shutil.rmtree(empty_dir) 