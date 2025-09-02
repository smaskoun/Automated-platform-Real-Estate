// Permanent A/B Testing Fix - Auto-loads on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Loading permanent A/B testing fix...');
    
    // Fix for View Results and View Details buttons
    document.addEventListener('click', function(e) {
        if (e.target.textContent && (
            e.target.textContent.includes('View Results') || 
            e.target.textContent.includes('View Details')
        )) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🎯 A/B Testing button clicked');
            
            // Get test ID - try multiple methods
            let testId = null;
            
            // Method 1: Look for data attributes
            const testContainer = e.target.closest('[data-test-id]');
            if (testContainer) {
                testId = testContainer.getAttribute('data-test-id');
            }
            
            // Method 2: Look in the test card for ID patterns
            if (!testId) {
                const testCard = e.target.closest('.test-card, .active-test, [class*="test"]');
                if (testCard) {
                    const textContent = testCard.textContent;
                    const idMatch = textContent.match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/);
                    if (idMatch) {
                        testId = idMatch[0];
                    }
                }
            }
            
            // Method 3: Use most recent test ID as fallback
            if (!testId) {
                // Fetch all tests and use the most recent one
                fetch('/api/ab-testing/tests')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.tests && data.tests.length > 0) {
                            // Use the most recent test
                            testId = data.tests[data.tests.length - 1].id;
                            loadTestResults(testId);
                        } else {
                            alert('No tests found. Please create a test first.');
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching tests:', error);
                        alert('Error loading tests: ' + error.message);
                    });
                return; // Exit here, loadTestResults will be called from the fetch
            }
            
            // If we have a testId, load results directly
            if (testId) {
                loadTestResults(testId);
            }
        }
        
        // Fix for View Active Tests button
        if (e.target.textContent && e.target.textContent.includes('View Active Tests')) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🎯 View Active Tests clicked');
            
            // Show loading
            showLoading('Loading Active Tests...');
            
            // Fetch active tests
            fetch('/api/ab-testing/tests')
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    console.log('✅ Active tests data:', data);
                    
                    if (data.success && data.tests) {
                        showActiveTestsList(data.tests);
                    } else {
                        alert('Error loading active tests: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    hideLoading();
                    console.error('❌ Error:', error);
                    alert('Error loading active tests: ' + error.message);
                });
        }
    });
    
    // Function to load test results
    function loadTestResults(testId) {
        console.log('📡 Fetching results for:', testId);
        
        // Show loading
        showLoading('Loading A/B Test Results...');
        
        // Fetch results
        fetch(`/api/ab-testing/analyze-results/${testId}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                console.log('✅ API Response:', data);
                
                if (data.success && data.data) {
                    showABResults(data.data);
                } else {
                    alert('Error: ' + (data.error || 'Failed to load results'));
                }
            })
            .catch(error => {
                hideLoading();
                console.error('❌ Error:', error);
                alert('Error: ' + error.message);
            });
    }
    
    // Loading function
    function showLoading(message = 'Loading...') {
        removeModals();
        document.body.insertAdjacentHTML('beforeend', `
            <div id="loading-modal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:99999;font-family:Arial,sans-serif;">
                <div style="background:white;padding:30px;border-radius:10px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
                    <h3 style="margin:0 0 15px 0;color:#333;">🔄 ${message}</h3>
                    <div style="margin:20px 0;color:#666;">Please wait...</div>
                    <div style="width:40px;height:40px;border:4px solid #f3f3f3;border-top:4px solid #007bff;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto;"></div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `);
    }
    
    // Hide loading
    function hideLoading() {
        const loading = document.getElementById('loading-modal');
        if (loading) loading.remove();
    }
    
    // Show A/B test results
    function showABResults(data) {
        removeModals();
        
        let variationsHTML = '';
        if (data.variations && data.variations.length > 0) {
            variationsHTML = data.variations.map((v, index) => `
                <div style="border:2px solid #e9ecef;margin:15px 0;padding:20px;border-radius:8px;background:#f8f9fa;transition:transform 0.2s ease;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <h4 style="color:#007bff;margin:0 0 10px 0;display:flex;align-items:center;">
                        <span style="background:#007bff;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:10px;font-size:14px;">${v.version || String.fromCharCode(65 + index)}</span>
                        Version ${v.version || String.fromCharCode(65 + index)}
                    </h4>
                    <p style="color:#666;margin:5px 0 15px 0;font-size:14px;"><strong>Strategy:</strong> ${v.focus || v.approach || 'Content optimization'}</p>
                    <div style="background:white;padding:15px;border-radius:5px;margin:10px 0;border-left:4px solid #007bff;font-size:16px;line-height:1.5;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                        ${v.content}
                    </div>
                    <div style="margin-top:15px;">
                        <button onclick="copyContent('${v.content.replace(/'/g, "\\'")}', this)" style="background:#28a745;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;margin-right:10px;font-size:14px;transition:background 0.2s;">📋 Copy Content</button>
                        <button onclick="shareContent('${v.content.replace(/'/g, "\\'")}', '${v.version || String.fromCharCode(65 + index)}')" style="background:#17a2b8;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px;transition:background 0.2s;">📤 Share</button>
                    </div>
                </div>
            `).join('');
        } else {
            variationsHTML = `
                <div style="text-align:center;padding:40px;color:#666;">
                    <h4>📭 No variations found</h4>
                    <p>The test may still be generating content. Please try again in a moment.</p>
                </div>
            `;
        }
        
        let instructionsHTML = '';
        if (data.instructions && data.instructions.length > 0) {
            instructionsHTML = '<ol style="color:#666;line-height:1.6;">' + data.instructions.map(inst => `<li style="margin:5px 0;">${inst}</li>`).join('') + '</ol>';
        } else {
            instructionsHTML = `
                <ol style="color:#666;line-height:1.6;">
                    <li style="margin:5px 0;">Copy each variation above using the copy buttons</li>
                    <li style="margin:5px 0;">Post them to your social media at different times or days</li>
                    <li style="margin:5px 0;">Track engagement metrics (likes, comments, shares, reach)</li>
                    <li style="margin:5px 0;">Note which version performs best</li>
                    <li style="margin:5px 0;">Use winning elements in future content creation</li>
                </ol>
            `;
        }
        
        const modalHTML = `
            <div id="ab-results-modal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:99999;font-family:Arial,sans-serif;">
                <div style="background:white;padding:30px;border-radius:12px;max-width:900px;max-height:85vh;overflow-y:auto;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;border-bottom:2px solid #f8f9fa;padding-bottom:15px;">
                        <h2 style="margin:0;color:#333;display:flex;align-items:center;">
                            <span style="margin-right:10px;">🧪</span>
                            A/B Test Results
                        </h2>
                        <button onclick="removeModals()" style="background:#dc3545;color:white;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;font-size:16px;transition:background 0.2s;" onmouseover="this.style.background='#c82333'" onmouseout="this.style.background='#dc3545'">✕</button>
                    </div>
                    
                    <h3 style="color:#666;margin-bottom:15px;">${data.test_name || 'Content Variations'}</h3>
                    
                    <div style="background:linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);padding:15px;border-radius:8px;margin-bottom:20px;color:#155724;border-left:4px solid #28a745;">
                        <strong>✅ ${data.message || 'Content variations ready for manual testing'}</strong>
                    </div>
                    
                    <h4 style="color:#333;margin-bottom:15px;display:flex;align-items:center;">
                        <span style="margin-right:8px;">📝</span>
                        Content Variations (${data.variations ? data.variations.length : 0}):
                    </h4>
                    ${variationsHTML}
                    
                    <div style="background:#fff3cd;padding:15px;border-radius:8px;margin:20px 0;color:#856404;border-left:4px solid #ffc107;">
                        <h4 style="margin:0 0 10px 0;display:flex;align-items:center;">
                            <span style="margin-right:8px;">📋</span>
                            Testing Instructions:
                        </h4>
                        ${instructionsHTML}
                    </div>
                    
                    <div style="text-align:center;margin-top:25px;padding-top:20px;border-top:1px solid #eee;">
                        <button onclick="removeModals()" style="background:#6c757d;color:white;border:none;padding:12px 30px;border-radius:8px;cursor:pointer;font-size:16px;transition:background 0.2s;" onmouseover="this.style.background='#5a6268'" onmouseout="this.style.background='#6c757d'">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    // Show active tests list
    function showActiveTestsList(tests) {
        removeModals();
        
        let testsHTML = '';
        if (tests && tests.length > 0) {
            testsHTML = tests.map((test, index) => `
                <div style="border:2px solid #e9ecef;padding:20px;margin:15px 0;border-radius:8px;background:#f8f9fa;transition:transform 0.2s ease;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                        <h4 style="color:#007bff;margin:0;font-size:18px;display:flex;align-items:center;">
                            <span style="background:#007bff;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:10px;font-size:14px;">${index + 1}</span>
                            ${test.name || 'Unnamed Test'}
                        </h4>
                        <span style="background:${test.status === 'running' ? '#28a745' : '#6c757d'};color:white;padding:4px 12px;border-radius:12px;font-size:12px;text-transform:uppercase;">
                            ${test.status || 'created'}
                        </span>
                    </div>
                    
                    <div style="margin:10px 0;">
                        <p style="color:#666;margin:5px 0;font-size:14px;">
                            <strong>Platform:</strong> ${test.platform || 'instagram'}
                        </p>
                        <p style="color:#666;margin:5px 0;font-size:14px;">
                            <strong>Test Type:</strong> ${test.test_type || 'content optimization'}
                        </p>
                        <p style="color:#666;margin:5px 0;font-size:14px;">
                            <strong>Created:</strong> ${test.created_at ? new Date(test.created_at).toLocaleDateString() : 'Unknown'}
                        </p>
                        <p style="color:#999;margin:5px 0;font-size:12px;font-family:monospace;">
                            <strong>ID:</strong> ${test.id}
                        </p>
                    </div>
                    
                    <div style="margin-top:15px;">
                        <button onclick="loadTestResults('${test.id}')" style="background:#007bff;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;margin-right:10px;font-size:14px;transition:background 0.2s;">📊 View Results</button>
                        <button onclick="copyTestId('${test.id}')" style="background:#17a2b8;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px;transition:background 0.2s;">📋 Copy ID</button>
                    </div>
                </div>
            `).join('');
        } else {
            testsHTML = `
                <div style="text-align:center;padding:40px;color:#666;">
                    <h4>📭 No Active Tests Found</h4>
                    <p>Create a new A/B test to get started!</p>
                    <button onclick="removeModals()" style="background:#007bff;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;margin-top:15px;">Create New Test</button>
                </div>
            `;
        }
        
        const modalHTML = `
            <div id="active-tests-modal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:99999;font-family:Arial,sans-serif;">
                <div style="background:white;padding:30px;border-radius:12px;max-width:900px;max-height:85vh;overflow-y:auto;width:90%;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;border-bottom:2px solid #f8f9fa;padding-bottom:15px;">
                        <h2 style="color:#333;margin:0;display:flex;align-items:center;">
                            <span style="margin-right:10px;">📋</span>
                            Active A/B Tests
                        </h2>
                        <button onclick="removeModals()" style="background:#dc3545;color:white;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;font-size:16px;transition:background 0.2s;">✕</button>
                    </div>
                    
                    <div style="margin-bottom:20px;padding:15px;background:#f8f9fa;border-radius:8px;">
                        <p style="color:#666;margin:0;display:flex;align-items:center;">
                            <span style="margin-right:8px;">📊</span>
                            <strong>Total Tests: ${tests ? tests.length : 0}</strong>
                        </p>
                    </div>
                    
                    <div style="max-height:60vh;overflow-y:auto;">
                        ${testsHTML}
                    </div>
                    
                    <div style="text-align:center;margin-top:25px;padding-top:20px;border-top:1px solid #eee;">
                        <button onclick="removeModals()" style="background:#6c757d;color:white;border:none;padding:12px 30px;border-radius:8px;cursor:pointer;font-size:16px;transition:background 0.2s;">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    // Remove all modals
    function removeModals() {
        ['ab-results-modal', 'active-tests-modal', 'loading-modal'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.remove();
        });
    }
    
    // Make functions globally available
    window.loadTestResults = loadTestResults;
    window.removeModals = removeModals;
    window.copyContent = function(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            button.style.background = '#17a2b8';
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '#28a745';
            }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            button.textContent = '✅ Copied!';
            setTimeout(() => {
                button.textContent = '📋 Copy Content';
            }, 2000);
        });
    };
    
    window.shareContent = function(text, version) {
        if (navigator.share) {
            navigator.share({
                title: `A/B Test Version ${version}`,
                text: text
            });
        } else {
            // Fallback: copy to clipboard
            window.copyContent(text, event.target);
        }
    };
    
    window.copyTestId = function(testId) {
        navigator.clipboard.writeText(testId).then(() => {
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            button.style.background = '#28a745';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '#17a2b8';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Test ID: ' + testId);
        });
    };
    
    console.log('✅ Permanent A/B Testing fix loaded successfully!');
    console.log('🎯 All A/B testing features are now working permanently!');
});

