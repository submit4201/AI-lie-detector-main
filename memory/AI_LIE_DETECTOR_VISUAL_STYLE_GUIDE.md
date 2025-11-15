# AI Lie Detector - Visual Style Guide

## **Design Philosophy**

The AI Lie Detector app employs a **modern dark theme with glassmorphism aesthetics**, creating a sophisticated, high-tech interface that conveys trust and technological advancement. The design balances visual appeal with functional clarity, ensuring users can easily interpret complex analytical data.

---

## **Color Palette & Theme System**

### **Primary Color Scheme**
- **Base Background**: Dark slate gradient (`from-slate-900 via-purple-900 to-slate-900`)
- **Color Space**: OKLCH (Oklab) for consistent perceptual uniformity
- **Accent Colors**: Blue, purple, and cyan spectrum for a cohesive tech aesthetic

### **Color-Coded Risk Assessment System**
```
🟢 GREEN (High Credibility): 70-100 score
   - Low risk, high trustworthiness
   - Colors: green-500, green-600, emerald-600

🟡 YELLOW (Medium Credibility): 40-69 score  
   - Moderate risk, cautious assessment
   - Colors: yellow-500, amber-500, orange-500

🔴 RED (Low Credibility): 0-39 score
   - High risk, potential deception
   - Colors: red-500, red-600, red-700
```

### **Semantic Color Assignments**
- **Success/Positive**: Green spectrum (`green-300`, `green-500`, `emerald-600`)
- **Warning/Caution**: Yellow/Orange spectrum (`yellow-300`, `amber-500`, `orange-400`)
- **Error/Risk**: Red spectrum (`red-300`, `red-500`, `red-600`)
- **Info/Neutral**: Blue spectrum (`blue-300`, `blue-500`, `cyan-400`)
- **Accent/Interactive**: Purple spectrum (`purple-400`, `purple-600`, `indigo-600`)

---

## **Glassmorphism Design System**

### **Core Glassmorphism Elements**
```css
backdrop-blur-sm    /* Light blur effect */
backdrop-blur-md    /* Medium blur effect */
backdrop-blur-lg    /* Heavy blur effect */

bg-white/10         /* 10% white transparency */
bg-black/20         /* 20% black transparency */
bg-black/30         /* 30% black transparency */
```

### **Border & Shadow System**
- **Primary Borders**: `border-white/20` (20% white transparency)
- **Accent Borders**: `border-{color}-400/30` (30% colored transparency)
- **Hover States**: `border-{color}-400/50` (50% colored transparency)
- **Shadows**: `shadow-xl`, `shadow-2xl` for depth

---

## **Typography System**

### **Font Stack**
```css
font-family: system-ui, Avenir, Helvetica, Arial, sans-serif
```

### **Text Hierarchy**
- **Main Headers**: `text-5xl font-bold` with gradient text effects
- **Section Headers**: `text-2xl font-bold text-white`
- **Subsection Headers**: `text-xl font-semibold text-white`
- **Card Titles**: `text-lg font-semibold text-{color}-300`
- **Body Text**: `text-gray-200`, `text-gray-300`
- **Metadata**: `text-xs text-gray-400`

### **Gradient Text Effects**
```css
bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent
```

---

## **Component Design Patterns**

### **Card System**
```css
/* Primary Card Style */
bg-white/10 backdrop-blur-md border-white/20 shadow-xl

/* Themed Cards */
bg-gradient-to-br from-{color}-900/20 to-{color}-800/20 
backdrop-blur-sm border-{color}-400/30
```

### **Interactive Elements**

#### **Buttons**
- **Primary**: `bg-gradient-to-r from-blue-600 to-purple-600`
- **Success**: `bg-gradient-to-r from-green-600 to-emerald-600`
- **Warning**: `bg-gradient-to-r from-red-600 to-red-700`
- **Hover Effects**: Color shift and `shadow-xl` enhancement

#### **Progress Bars**
```css
/* Background Track */
bg-black/30 rounded-full

/* Progress Fill */
bg-gradient-to-r from-{color}-600 to-{color}-400
```

#### **Metric Cards**
```css
bg-black/20 backdrop-blur-sm border-{color}-400/30
hover:border-{color}-400/50 transition-all
```

---

## **Layout & Grid System**

### **Responsive Grid Patterns**
- **Desktop**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- **Metrics**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- **Key Highlights**: `md:col-span-2 lg:col-span-3` for spanning cells

### **Spacing System**
- **Container Padding**: `p-6` (24px)
- **Component Spacing**: `space-y-6` (24px vertical)
- **Element Gaps**: `gap-4`, `gap-6` (16px, 24px)
- **Content Margins**: `mb-4`, `mb-6` (16px, 24px)

---

## **Animation & Transitions**

### **Standard Transitions**
```css
transition-all duration-300    /* General interactions */
transition-all duration-500    /* Data visualizations */
transition-all duration-700    /* Chart animations */
```

### **Loading States**
- **Spinner**: `animate-spin` with `Loader2` icon
- **Progress Bars**: Smooth width transitions
- **Backdrop Blur**: Gradual opacity changes

### **Hover Effects**
- **Border Enhancement**: Opacity increase (30% → 50%)
- **Background Shift**: Slight opacity/color changes
- **Shadow Addition**: `hover:shadow-lg`, `hover:shadow-xl`
- **Icon Scaling**: Subtle transform effects

---

## **Data Visualization**

### **Chart Color Palette**
```css
--chart-1: oklch(0.488 0.243 264.376)  /* Blue */
--chart-2: oklch(0.696 0.17 162.48)    /* Green */
--chart-3: oklch(0.769 0.188 70.08)    /* Yellow */
--chart-4: oklch(0.627 0.265 303.9)    /* Purple */
--chart-5: oklch(0.645 0.246 16.439)   /* Orange */
```

### **Progress Visualization**
- **Radial Charts**: Semi-circular design with center labels
- **Bar Charts**: Gradient fills with hover tooltips
- **Timeline**: Connected dots with colored backgrounds
- **Credibility Meters**: Horizontal progress bars with risk color coding

---

## **Iconography System**

### **Emoji Icons for Context**
- **🎙️** Audio/Recording
- **📊** Analytics/Charts
- **🎯** Accuracy/Targeting
- **⚠️** Warnings/Alerts
- **🚩** Red Flags/Issues
- **✅** Success/Validation
- **🧠** AI/Intelligence
- **💬** Communication/Speech
- **📈** Trends/Growth
- **🔍** Analysis/Investigation

### **Lucide React Icons**
- **Navigation**: `Settings`, `Download`, `UploadCloud`
- **Media**: `Mic`, `StopCircle`, `Play`
- **Status**: `Loader2`, `CheckCircle`, `AlertTriangle`

---

## **Responsive Breakpoints**

### **Tailwind Breakpoint System**
```css
sm:   640px and up    /* Small devices */
md:   768px and up    /* Medium devices */
lg:   1024px and up   /* Large devices */
xl:   1280px and up   /* Extra large devices */
```

### **Adaptive Layouts**
- **Mobile First**: Stack vertically with full-width cards
- **Tablet**: 2-column grid with adjusted spacing
- **Desktop**: 3-4 column grid with complex layouts
- **Ultra-wide**: Maximum container width of 1280px

---

## **Accessibility Features**

### **Color Contrast**
- **High Contrast**: White text on dark backgrounds
- **Color Independence**: Meaningful without color (icons, text labels)
- **Status Indicators**: Multiple visual cues (color + text + icons)

### **Interactive States**
```css
focus:outline-4px auto -webkit-focus-ring-color
hover:border-color transition
active:transform scale-95
```

### **Screen Reader Support**
- Semantic HTML structure
- Descriptive alt text for visual elements
- ARIA labels for complex interactions

---

## **Brand Identity Elements**

### **Logo/Header Design**
```css
/* Gradient brand text */
bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 
bg-clip-text text-transparent
```

### **Application Branding**
- **Primary Title**: "🎙️ AI Lie Detector"
- **Tagline**: "Advanced voice analysis with AI-powered deception detection"
- **Color Identity**: Blue-purple-cyan spectrum
- **Visual Metaphors**: Microphone, brain, targeting, analysis charts

---

## **Implementation Guidelines**

### **CSS Custom Properties**
The app uses CSS custom properties with OKLCH color space for consistent theming:
```css
--radius: 0.625rem
--background: oklch(0.145 0 0)
--foreground: oklch(0.985 0 0)
```

### **Component Architecture**
- **Atomic Design**: Reusable metric cards, buttons, progress bars
- **Themed Variants**: Color-coded components for different data types
- **Responsive Utilities**: Tailwind classes for adaptive design

### **Performance Considerations**
- **Backdrop Filter**: Used judiciously for visual hierarchy
- **Gradient Optimization**: Efficient CSS gradients
- **Animation Performance**: Transform-based animations for smoothness

---

This visual style guide ensures consistency across the AI Lie Detector application while maintaining the sophisticated, tech-forward aesthetic that builds user trust in the analytical capabilities of the system.
