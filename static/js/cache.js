/* ==========================================
   CLIENT-SIDE CACHE MANAGER
   ========================================== */

class CacheManager {
    constructor() {
        this.cache = new Map();
        this.maxAge = 5 * 60 * 1000; // 5 minutes default
        this.maxSize = 50; // Maximum number of cached items
    }
    
    // Generate cache key
    generateKey(url, params = {}) {
        const paramString = Object.keys(params)
            .sort()
            .map(key => `${key}=${params[key]}`)
            .join('&');
        return `${url}?${paramString}`;
    }
    
    // Set cache item
    set(key, data, maxAge = this.maxAge) {
        // Remove oldest item if cache is full
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, {
            data: data,
            timestamp: Date.now(),
            maxAge: maxAge
        });
    }
    
    // Get cache item
    get(key) {
        const item = this.cache.get(key);
        
        if (!item) return null;
        
        // Check if item has expired
        if (Date.now() - item.timestamp > item.maxAge) {
            this.cache.delete(key);
            return null;
        }
        
        return item.data;
    }
    
    // Clear specific cache item
    clear(key) {
        this.cache.delete(key);
    }
    
    // Clear all cache
    clearAll() {
        this.cache.clear();
    }
    
    // Get cache size
    size() {
        return this.cache.size;
    }
    
    // Prune expired items
    prune() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now - item.timestamp > item.maxAge) {
                this.cache.delete(key);
            }
        }
    }
}

// Create global cache instance
const clientCache = new CacheManager();

// Prune cache every minute
setInterval(() => clientCache.prune(), 60000);

/* ==========================================
   FETCH WITH CACHE
   ========================================== */

async function fetchWithCache(url, options = {}) {
    const { 
        cache = true, 
        maxAge = 5 * 60 * 1000,
        forceRefresh = false,
        ...fetchOptions 
    } = options;
    
    const cacheKey = clientCache.generateKey(url, fetchOptions);
    
    // Check cache first if not forcing refresh
    if (cache && !forceRefresh) {
        const cachedData = clientCache.get(cacheKey);
        if (cachedData) {
            console.log(`📦 Cache hit for: ${url}`);
            return { 
                ...cachedData, 
                fromCache: true 
            };
        }
    }
    
    console.log(`🌐 Fetching: ${url}`);
    
    try {
        const response = await fetch(url, {
            ...fetchOptions,
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                ...fetchOptions.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Cache the successful response
        if (cache) {
            clientCache.set(cacheKey, data, maxAge);
        }
        
        return { 
            ...data, 
            fromCache: false 
        };
    } catch (error) {
        console.error(`❌ Fetch error for ${url}:`, error);
        
        // Try to return cached data on error
        if (cache) {
            const cachedData = clientCache.get(cacheKey);
            if (cachedData) {
                console.log(`📦 Returning stale cache due to error`);
                return { 
                    ...cachedData, 
                    fromCache: true, 
                    stale: true 
                };
            }
        }
        
        throw error;
    }
}

/* ==========================================
   PREFETCH MANAGER
   ========================================== */

class PrefetchManager {
    constructor() {
        this.queue = [];
        this.isProcessing = false;
    }
    
    // Add URL to prefetch queue
    add(url, options = {}) {
        this.queue.push({ url, options });
        this.process();
    }
    
    // Process prefetch queue
    async process() {
        if (this.isProcessing || this.queue.length === 0) return;
        
        this.isProcessing = true;
        
        while (this.queue.length > 0) {
            const { url, options } = this.queue.shift();
            
            try {
                await fetchWithCache(url, { 
                    ...options, 
                    cache: true 
                });
                
                // Small delay between prefetches
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                console.error(`Prefetch failed for ${url}:`, error);
            }
        }
        
        this.isProcessing = false;
    }
}

const prefetchManager = new PrefetchManager();

/* ==========================================
   EXPORT
   ========================================== */

window.CacheManager = CacheManager;
window.clientCache = clientCache;
window.fetchWithCache = fetchWithCache;
window.prefetchManager = prefetchManager;
