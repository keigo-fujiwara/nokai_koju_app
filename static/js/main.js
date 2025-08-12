// メインJavaScriptファイル

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // アラートの自動非表示
    initializeAlerts();
    
    // ドロップダウンの初期化
    initializeDropdowns();
    
    // スライドショーの初期化（ホームページのみ）
    if (document.querySelector('.preview-question')) {
        window.previewSlideshow = new PreviewSlideshow();
    }
});

// アラートの自動非表示機能
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // 5秒後に自動で非表示
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease-out';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert && alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        }, 5000);
    });
}

// ドロップダウンの初期化
function initializeDropdowns() {
    // Bootstrapのドロップダウンが正しく動作するかチェック
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    console.log('Found dropdowns:', dropdowns.length);
    
    dropdowns.forEach((dropdown, index) => {
        console.log(`Dropdown ${index}:`, dropdown);
        
        // クリックイベントが正しく動作するかテスト
        dropdown.addEventListener('click', function(e) {
            console.log('Dropdown clicked:', this.textContent);
        });
    });
}

// ユーティリティ関数
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        initializeAlerts();
    }
}

// フォームのバリデーション
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 数値のフォーマット
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 日付のフォーマット
function formatDate(date) {
    const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString('ja-JP', options);
}

// スライドショー機能
class PreviewSlideshow {
    constructor() {
        this.currentSlide = 0; // 初回表示フラグとして0を使用
        this.totalSlides = 6;
        this.interval = null;
        this.slideDuration = 4000; // 4秒（スライド効果を見やすくするため）
        this.init();
    }
    
    init() {
        // 初回表示の設定
        this.showSlide(1);
        
        // スライドショー開始（少し遅延）
        setTimeout(() => {
            this.startSlideshow();
        }, 500);
        
        this.setupIndicators();
    }
    
    startSlideshow() {
        this.interval = setInterval(() => {
            this.nextSlide();
        }, this.slideDuration);
    }
    
    nextSlide() {
        // 次のスライド番号を計算
        const nextSlideNumber = this.currentSlide >= this.totalSlides ? 1 : this.currentSlide + 1;
        this.showSlide(nextSlideNumber);
    }
    
    showSlide(slideNumber) {
        const slides = document.querySelectorAll('.preview-question');
        const indicators = document.querySelectorAll('.indicator');
        
        // 現在のアクティブスライドを取得
        const currentActiveSlide = document.querySelector('.preview-question.active');
        
        // 全てのスライドとインジケーターをリセット
        slides.forEach(slide => {
            slide.classList.remove('active', 'prev', 'next');
        });
        
        indicators.forEach(indicator => {
            indicator.classList.remove('active');
        });
        
        // 新しいスライドを取得
        const targetSlide = document.querySelector(`[data-slide="${slideNumber}"]`);
        const targetIndicator = document.querySelector(`.indicator[data-slide="${slideNumber}"]`);
        
        if (targetSlide && currentActiveSlide && this.currentSlide !== 0) {
            // スライド方向を決定（初回表示以外）
            const currentSlideNumber = parseInt(currentActiveSlide.getAttribute('data-slide'));
            const direction = slideNumber > currentSlideNumber ? 'next' : 'prev';
            
            // 現在のスライドを反対方向に移動
            currentActiveSlide.classList.add(direction === 'next' ? 'prev' : 'next');
            
            // 新しいスライドをアクティブに
            targetSlide.classList.add('active');
        } else if (targetSlide) {
            // 初回表示または直接指定
            targetSlide.classList.add('active');
        }
        
        // インジケーターを更新
        if (targetIndicator) {
            targetIndicator.classList.add('active');
        }
        
        this.currentSlide = slideNumber;
    }
    
    setupIndicators() {
        document.querySelectorAll('.indicator').forEach(indicator => {
            indicator.addEventListener('click', (e) => {
                e.preventDefault();
                const slideNumber = parseInt(indicator.getAttribute('data-slide'));
                this.showSlide(slideNumber);
                
                // クリック時にスライドショーをリセット
                clearInterval(this.interval);
                this.startSlideshow();
            });
        });
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}
