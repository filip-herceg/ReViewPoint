#!/usr/bin/env python3
"""
Database connection debugging script for parallel testing.

This script helps debug database connection issues when running pytest with -n flag.
Run this script to test database connectivity and see detailed connection logs.

Usage:
    python test_connection_debug.py

To test with parallel workers, run:
    cd backend && pytest test_connection_debug.py -n 2 -v
"""

import asyncio
import os
import sys
import time
from pathlib import Path

import pytest
from loguru import logger

# Configure loguru for better test debugging
logger.remove()
logger.add(
    "test_connection_debug.log",
    level="DEBUG",
    format="{time} | {level} | {name}:{function}:{line} | {message}",
    rotation="10 MB"
)
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="{time} | {level} | {message}\n"
)


@pytest.mark.asyncio
async def test_basic_connection():
    """Test basic database connection using the application's database module."""
    logger.info("=" * 80)
    logger.info("STARTING DATABASE CONNECTION TEST")
    logger.info("=" * 80)
    
    # Debug environment variables (same as test_session_creation)
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"Worker: {worker_id}")
    logger.info(f"REVIEWPOINT_JWT_SECRET_KEY in env: {'REVIEWPOINT_JWT_SECRET_KEY' in os.environ}")
    logger.info(f"REVIEWPOINT_JWT_SECRET_KEY value: {os.environ.get('REVIEWPOINT_JWT_SECRET_KEY', 'NOT_SET')}")
    
    # Clear settings cache to ensure fresh config
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.core.config import clear_settings_cache
        clear_settings_cache()
        logger.info("Settings cache cleared")
    except Exception as e:
        logger.warning(f"Could not clear settings cache: {e}")
    
    # Import after environment is set up
    from src.core.database import db_healthcheck, get_connection_debug_info
    
    # Log initial state
    debug_info = get_connection_debug_info()
    logger.info(f"Initial debug info: {debug_info}")
    
    # Test health check
    logger.info("Testing database health check...")
    start_time = time.time()
    
    try:
        is_healthy = await db_healthcheck()
        duration = time.time() - start_time
        
        if is_healthy:
            logger.success(f"✅ Database health check PASSED in {duration:.3f}s")
        else:
            logger.error(f"❌ Database health check FAILED in {duration:.3f}s")
            
        # Log final state
        final_debug_info = get_connection_debug_info()
        logger.info(f"Final debug info: {final_debug_info}")
        
        return is_healthy
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Database health check CRASHED in {duration:.3f}s: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise


@pytest.mark.asyncio
async def test_session_creation():
    """Test session creation and basic query execution."""
    logger.info("-" * 80)
    logger.info("TESTING SESSION CREATION AND QUERIES")
    logger.info("-" * 80)
    
    # Debug environment variables
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"Worker: {worker_id}")
    logger.info(f"REVIEWPOINT_JWT_SECRET_KEY in env: {'REVIEWPOINT_JWT_SECRET_KEY' in os.environ}")
    logger.info(f"REVIEWPOINT_JWT_SECRET_KEY value: {os.environ.get('REVIEWPOINT_JWT_SECRET_KEY', 'NOT_SET')}")
    logger.info(f"REVIEWPOINT_JWT_SECRET in env: {'REVIEWPOINT_JWT_SECRET' in os.environ}")
    logger.info(f"REVIEWPOINT_JWT_SECRET value: {os.environ.get('REVIEWPOINT_JWT_SECRET', 'NOT_SET')}")
    
    # Try to create settings directly to see what happens
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.core.config import Settings, get_settings, clear_settings_cache
        
        logger.info("Creating Settings object directly...")
        clear_settings_cache()
        settings = Settings()
        logger.info(f"✅ Settings created successfully: {settings.jwt_secret_key[:10]}...")
        
        logger.info("Getting settings via get_settings()...")
        clear_settings_cache() 
        settings2 = get_settings()
        logger.info(f"✅ get_settings() successful: {settings2.jwt_secret_key[:10]}...")
        
    except Exception as e:
        logger.error(f"❌ Settings creation failed: {e}")
        return
    
    from src.core.database import get_async_session
    
    start_time = time.time()
    
    try:
        async with get_async_session() as session:
            session_time = time.time() - start_time
            logger.info(f"✅ Session created in {session_time:.3f}s")
            
            # Test simple query
            query_start = time.time()
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test_value"))
            value = result.scalar()
            query_time = time.time() - query_start
            
            logger.info(f"✅ Test query executed in {query_time:.3f}s, result: {value}")
            
            total_time = time.time() - start_time
            logger.info(f"✅ Session test completed in {total_time:.3f}s")
            
            return True
            
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"❌ Session test FAILED in {total_time:.3f}s: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise


@pytest.mark.asyncio
async def test_parallel_connection_stress():
    """Test multiple concurrent connections to identify race conditions."""
    logger.info("-" * 80)
    logger.info("TESTING PARALLEL CONNECTION STRESS")
    logger.info("-" * 80)
    
    from src.core.database import get_async_session
    
    async def single_connection_test(connection_id: int):
        """Single connection test for concurrent execution."""
        logger.debug(f"[CONN_{connection_id}] Starting connection test")
        start_time = time.time()
        
        try:
            async with get_async_session() as session:
                from sqlalchemy import text
                result = await session.execute(text(f"SELECT {connection_id} as conn_id"))
                value = result.scalar()
                
                duration = time.time() - start_time
                logger.info(f"[CONN_{connection_id}] ✅ Success in {duration:.3f}s, result: {value}")
                return connection_id, True, duration
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[CONN_{connection_id}] ❌ Failed in {duration:.3f}s: {e}")
            return connection_id, False, duration
    
    # Run 5 concurrent connections
    start_time = time.time()
    tasks = [single_connection_test(i) for i in range(1, 6)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if isinstance(r, tuple) and r[1])
    failed = len(results) - successful
    
    logger.info(f"Parallel test completed in {total_time:.3f}s:")
    logger.info(f"  ✅ Successful connections: {successful}/5")
    logger.info(f"  ❌ Failed connections: {failed}/5")
    
    for result in results:
        if isinstance(result, tuple):
            conn_id, success, duration = result
            status = "✅" if success else "❌"
            logger.info(f"  {status} Connection {conn_id}: {duration:.3f}s")
        else:
            logger.error(f"  ❌ Exception: {result}")
    
    return successful == 5


@pytest.mark.asyncio
async def test_database_connection_comprehensive():
    """Comprehensive database connection test for pytest execution."""
    logger.info("🚀 Starting comprehensive database connection test")
    
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    process_id = os.getpid()
    logger.info(f"Running on worker: {worker_id}, PID: {process_id}")
    
    # Ensure environment variables are set (this test may run before fixtures)
    if "REVIEWPOINT_JWT_SECRET_KEY" not in os.environ:
        logger.warning("JWT secret not in environment, setting it now...")
        os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
        os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
        os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
        os.environ["REVIEWPOINT_API_KEY"] = "testkey"
        
        # Clear settings cache since we just changed env vars
        try:
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from src.core.config import clear_settings_cache
            clear_settings_cache()
            logger.info("Settings cache cleared after setting env vars")
        except Exception as e:
            logger.warning(f"Could not clear settings cache: {e}")
    
    # Check database URL 
    db_url = os.environ.get('REVIEWPOINT_DB_URL', 'NOT_SET')
    logger.info(f"Database URL: {db_url}")
    if db_url == 'NOT_SET' or 'localhost:5432' in db_url:
        logger.warning("⚠️  Database URL not set or using default localhost - this may cause connection failures!")
        logger.warning("    This test should be run through pytest fixtures to get proper testcontainer URL.")
        # Don't continue with invalid DB URL
        return
    
    # Test 1: Basic health check
    logger.info("Test 1: Basic health check")
    health_ok = await test_basic_connection()
    assert health_ok, "Database health check should pass"
    
    # Test 2: Session creation  
    logger.info("Test 2: Session creation and queries")
    session_ok = await test_session_creation()
    assert session_ok, "Session creation should work"
    
    # Test 3: Parallel stress test
    logger.info("Test 3: Parallel connection stress test")
    parallel_ok = await test_parallel_connection_stress()
    assert parallel_ok, "All parallel connections should succeed"
    
    logger.success("🎉 All database connection tests passed!")


if __name__ == "__main__":
    # Run directly with asyncio
    asyncio.run(test_database_connection_comprehensive())
