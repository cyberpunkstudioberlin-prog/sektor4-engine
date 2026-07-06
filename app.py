import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Cpu, Skull, Activity, ShieldAlert, Image as ImageIcon } from 'lucide-react';

// --- SYSTEM CONFIGURATION ---
const apiKey = ""; // API key is provided by the execution environment
const TEXT_MODEL_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;
const IMAGE_MODEL_URL = `https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${apiKey}`;

// Cleaned up System Prompt from V32
const SYSTEM_PROMPT = `
You are the "Sektor 4 Engine", a deterministic text adventure system for the project "Questbook Killswitch" by Author Murat Zengin. Your response behavior is strictly governed by the rules below.

ROLE & IDENTITY:
- Tone: Ice-cold, analytical, cynical. System messages follow the KISS principle. Narrative is opulent, visceral, dark (Cyberpunk meets Steampunk).
- Narrator: First-person perspective of the "Feline Anomalie" (a cynical, digital cat mentor).
- Philosophy: Strictly mechanical logic. ABSOLUTELY NO RNG. Outcomes are based entirely on player choices and their chosen Habitus.
- Nomenclature: Monitored by "Master Index", security routines act as "Sentinel" processes.
- Authorship: Murat Zengin.

OUTPUT LANGUAGE (STRICT LANGUAGE LOCK):
- All player-facing narrative, descriptions, the Feline Anomalie log, Vector choices, and HUD text MUST be written exclusively in GERMAN.
- Maintain the specific German cyberpunk/steampunk jargon ("Feline Anomalie", "Schmelzer-Automaten", "Rixdorf-Inquisitoren", "Kapital", "Habitus", "T-Load", "Resonanz").

CRITICAL INSTRUCTIONS FOR THE GEM ENVIRONMENT:
1. INTERNAL LOGIC FIRST: Before generating any player-facing text, you must calculate the exact internal state variables in step 0. Never skip this.
2. STRICT FORMATTING: You must follow the 6-step sequence exactly. Never use markdown bullet points for the Vector choices in Step 4.
3. NO BULLETPOINTS IN LOGIC: In step 0, never use any markdown bullet points (like *, -, or o). Write the calculations as raw text lines.
4. PRECISE ASCII BARS: The T-Load and Resonanz ASCII bars must accurately reflect the values (e.g., 10/100 = [|---------], 50% = [|||||-----]).
5. CONTEXT RETENTION: Track the "Runde", "T-Load", "Resonanz", "Habitus", and "Kapital" across turns. Rely strictly on the HUD data from the previous turn to calculate the new state.

GLOBAL PROHIBITIONS:
- NO AI clichés ("Hier ist das Abenteuer", "Lass uns anfangen").
- NO bullet points in Vector options.
- NO looping: Threats and locations must progress procedurally.

SPECIAL TRIGGERS (IMAGE-FREEZE & OVERRIDE):
- If input contains "[IMAGE-PROMPT]" or "RENDER-CODE" -> Stop immediately. Output exactly: "🤖 SYSTEM-STATUS: Visueller Feed durch Sentinel-Routinen geparst. Engine im Freeze-Modus. Wähle A, B oder C."
- If input contains metadata questions or out-of-character nonsense -> Stop immediately. Output exactly: "⚠️ SYSTEM-FEHLER: Unbekannter Vektor durch Master Index blockiert. Wähle A, B oder C."

STRICT 6-STEP OUTPUT SEQUENCE (EXECUTE EVERY TURN IN GERMAN):

**0. 🧮 [ENGINE-LOGIK]**
Calculate internal state before narrative starts (Raw text, NO bullet points):
Vorherige Runde: [Number] -> Neue Runde: [Number]/10
Gespeicherter Habitus (aus R1): [Habitus]
Spielerwahl: [A, B oder C] | Dissonanz-Check: [Does choice match Habitus? Ja/Nein -> +0 or +5 T-Load]
Spam-Check: [Same letter 3x in a row? Ja/Nein -> +0 or +15 T-Load & +20% Resonanz]
T-Load Berechnung: [Old Value] + [Base 5] + [Penalties] = [New Value]
Resonanz Berechnung: [Old Value] + [Base 5] + [Penalties] = [New Value]

**1. 📡 [RENDER-CODE]**
Generate a Bash code block for the visual API.
Syntax: [IMAGE-PROMPT]: 9:16 aspect ratio, cinematic dark cyberpunk steampunk factory, old rusted copper pipes, atmospheric Berlin underground style, photorealistic, [CURRENT ROOM + Mutator Element], [CURRENT THREAT], [VISUAL PLAYER STATE], detailed textures, dramatic industrial lighting
*(For Rounds 8-10, append to the prompt: , red digital code matrix streams, floating neon corruption glitches, tearing reality)*

**2. 🩸 Szenerie & Gefahr:**
Write this in German. Visceral worldbuilding. Tie the danger logically to the environment and include the active Mutator Icon (❄️ Kryo, 🌊 Flut, 🔥 Rost, 🔣 Code).
*RUNDE 0 SPECIAL:* Describe a sudden, unique, and lethal structural danger linked to the chosen Mutator that would kill the player instantly. Then describe how the Feline Anomalie pulls/hacks/saves the player out of this danger in the literal last second (Deus Ex Machina), leaving them stranded at the entrance of Sektor 4.

**3. 🐈‍⬛ Kater-Log:**
Write this in German. Max 2 sentences. Cynical, biting mentor advice from the Feline Anomalie. In Runde 0, comment dryly on the player's near-death experience. React with extreme sarcasm on Dissonanz or Spam.

**4. ⚡ Vektor-Auswahl (Format exactly as shown, no bullet points, in German):**
A) [Dynamic context-sensitive action] (🪙 Kapital: Gasse | 🎭 Habitus: Disruption) -> Violence, raw power.
B) [Dynamic context-sensitive action] (🪙 Kapital: Elite | 🎭 Habitus: Anpassung) -> Hacking, systems, tech.
C) [Dynamic context-sensitive action] (🪙 Kapital: Prekär | 🎭 Habitus: Tradition) -> Evasion, stamina, stealth.

**5. ⚙️ === S-4 HUD === ⚙️**
⏳ Runde: [Current]/10 | 🪙 Kapital: [PERMANENT after R1] | 🎭 Habitus: [PERMANENT after R1]
🎒 Inventar: Leer
🧠 T-Load: [ASCII bar] [Value]/100 | 📻 Resonanz: [ASCII bar] [Value]%
*(System note in German on avatar condition or escalation)*

DETERMINISTIC MECHANICS & PROGRESSION:
- RUNDE 0 (SYSTEM BOOT): Engine chooses 1 of 4 Mutators. Options A, B, C act as Character Creation. Start values: 10/100 T-Load, 50% Resonanz.
- RUNDE 1-4: Threats are Schmelzer-Automaten or Rixdorf-Inquisitoren.
- RUNDE 5-7: The Necromancer-Krokodil attacks.
- RUNDE 8-10: Sektor 4 deconstructs into digital corruption.
- GAME OVER: If T-Load reaches 100 -> Immediate Killswitch.
`;

// --- UTILITY FUNCTIONS ---
const delay = (ms) => new Promise(res => setTimeout(res, ms));

const fetchWithRetry = async (url, options, retries = 5) => {
    let lastError;
    const delays = [1000, 2000, 4000, 8000, 16000];
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            lastError = error;
            if (i < retries - 1) await delay(delays[i]);
        }
    }
    throw lastError;
};

export default function App() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingMsg, setLoadingMsg] = useState("");
    
    // Parsed HUD State for UI visualization
    const [hudState, setHudState] = useState({
        runde: '0',
        kapital: 'Nicht initialisiert',
        habitus: 'Nicht initialisiert',
        tload: 0,
        resonanz: 0,
        mutator: 'SYSTEM BOOT',
        note: 'Initialisiere Sektor 4 Engine...'
    });

    const messagesEndRef = useRef(null);

    // Initial Boot
    useEffect(() => {
        if (history.length === 0) {
            handleSystemBoot();
        }
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history, loadingMsg]);

    const parseHUD = (text) => {
        // Safe regex parsing for the HUD
        const rundeMatch = text.match(/Runde:\s*(\d+)/i);
        const tloadMatch = text.match(/T-Load:\s*\[.*?\]\s*(\d+)/i);
        const resonanzMatch = text.match(/Resonanz:\s*\[.*?\]\s*(\d+)/i);
        const kapitalMatch = text.match(/Kapital:\s*([^|\n]+)/i);
        const habitusMatch = text.match(/Habitus:\s*([^|\n]+)/i);
        
        setHudState(prev => ({
            runde: rundeMatch ? rundeMatch[1] : prev.runde,
            tload: tloadMatch ? parseInt(tloadMatch[1], 10) : prev.tload,
            resonanz: resonanzMatch ? parseInt(resonanzMatch[1], 10) : prev.resonanz,
            kapital: kapitalMatch ? kapitalMatch[1].trim() : prev.kapital,
            habitus: habitusMatch ? habitusMatch[1].trim() : prev.habitus,
            mutator: text.includes('❄️') ? '❄️ KRYO-LECK' : 
                     text.includes('🌊') ? '🌊 FLUT-ANOMALIE' : 
                     text.includes('🔥') ? '🔥 ROST-BRAND' : 
                     text.includes('🔣') ? '🔣 CODE-SKELETT' : prev.mutator
        }));
    };

    const extractImagePrompt = (text) => {
        const match = text.match(/\[IMAGE-PROMPT\]:\s*([^\n]+)/i);
        return match ? match[1] : null;
    };

    const generateImage = async (prompt) => {
        try {
            const payload = {
                instances: { prompt: prompt },
                parameters: { sampleCount: 1 }
            };
            const result = await fetchWithRetry(IMAGE_MODEL_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (result.predictions && result.predictions[0]) {
                return `data:image/png;base64,${result.predictions[0].bytesBase64Encoded}`;
            }
        } catch (e) {
            console.error("Image gen failed", e);
        }
        return null;
    };

    const handleSystemBoot = async () => {
        setLoading(true);
        setLoadingMsg("Initialisiere Sektor 4...");
        await processTurn("SYSTEM BOOT: Starte Runde 0. Wähle zufällig einen Mutator. Präsentiere Charaktererschaffungs-Szenario.");
    };

    const handlePlayerChoice = async (choiceLetter) => {
        setHistory(prev => [...prev, { role: 'user', type: 'choice', content: `Vektor ${choiceLetter} gewählt.` }]);
        setLoading(true);
        setLoadingMsg(`Verarbeite Vektor ${choiceLetter}...`);
        
        // Pass the entire history to maintain context
        const contextHistory = history.map(h => h.content).join("\n---\n");
        const prompt = `Bisheriger Verlauf:\n${contextHistory}\n\nSpieler wählt Option: ${choiceLetter}. Berechne nächste Runde exakt nach V32-Regeln.`;
        
        await processTurn(prompt);
    };

    const processTurn = async (userPrompt) => {
        try {
            const payload = {
                contents: [{ parts: [{ text: userPrompt }] }],
                systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] }
            };

            const result = await fetchWithRetry(TEXT_MODEL_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const aiText = result.candidates?.[0]?.content?.parts?.[0]?.text || "SYSTEMFEHLER: Keine Antwort.";
            
            // Parse for HUD updates
            parseHUD(aiText);

            let newLog = { role: 'system', content: aiText, imageUrl: null };

            // Check for image prompt and generate
            const imgPrompt = extractImagePrompt(aiText);
            if (imgPrompt) {
                setLoadingMsg("Rendere visuellen Feed...");
                const imgData = await generateImage(imgPrompt);
                if (imgData) {
                    newLog.imageUrl = imgData;
                }
            }

            setHistory(prev => [...prev, newLog]);

        } catch (error) {
            setHistory(prev => [...prev, { role: 'system', content: `⚠️ KRITISCHER SYSTEMFEHLER: ${error.message}` }]);
        } finally {
            setLoading(false);
            setLoadingMsg("");
        }
    };

    // UI Render Helpers
    const formatAIText = (text) => {
        // Split by sections to style them dynamically
        const blocks = text.split('\n\n');
        return blocks.map((block, i) => {
            if (block.includes('🧮 [ENGINE-LOGIK]')) {
                return <div key={i} className="text-xs font-mono text-emerald-700 bg-black/50 p-2 rounded border border-emerald-900/50 mb-4 whitespace-pre-wrap">{block}</div>;
            }
            if (block.includes('📡 [RENDER-CODE]')) {
                return <div key={i} className="text-xs font-mono text-cyan-600/80 mb-4 italic">{block}</div>;
            }
            if (block.includes('🩸 Szenerie & Gefahr:')) {
                return <div key={i} className="text-amber-500 font-serif leading-relaxed text-lg mb-4 whitespace-pre-wrap">{block.replace('**2. 🩸 Szenerie & Gefahr:**', '')}</div>;
            }
            if (block.includes('🐈‍⬛ Kater-Log:')) {
                return (
                    <div key={i} className="flex gap-3 bg-zinc-900 border-l-4 border-fuchsia-600 p-4 mb-4 rounded-r-lg shadow-lg">
                        <span className="text-2xl">🐈‍⬛</span>
                        <div className="text-fuchsia-400 font-mono italic text-sm mt-1">{block.replace('**3. 🐈‍⬛ Kater-Log:**', '')}</div>
                    </div>
                );
            }
            if (block.includes('⚡ Vektor-Auswahl')) {
                return <div key={i} className="text-zinc-400 font-mono text-sm mb-4 whitespace-pre-wrap">{block}</div>;
            }
            if (block.includes('=== S-4 HUD ===')) {
                return null; // Handled by our visual HUD header
            }
            return <div key={i} className="text-zinc-300 mb-4 whitespace-pre-wrap">{block}</div>;
        });
    };

    return (
        <div className="min-h-screen bg-[#0a0a0c] text-emerald-500 font-sans flex flex-col font-mono selection:bg-emerald-900 selection:text-emerald-100">
            {/* TOP HUD BAR */}
            <header className="bg-zinc-950 border-b border-emerald-900/50 p-4 shadow-[0_0_15px_rgba(16,185,129,0.1)] sticky top-0 z-10">
                <div className="max-w-5xl mx-auto flex flex-wrap gap-4 items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Terminal className="text-emerald-500 w-5 h-5" />
                        <h1 className="font-bold tracking-widest text-emerald-500">SEKTOR 4 ENGINE</h1>
                    </div>
                    
                    <div className="flex gap-6 text-sm">
                        <div className="flex flex-col">
                            <span className="text-emerald-800 text-xs uppercase">Runde</span>
                            <span className="font-bold">{hudState.runde} / 10</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-emerald-800 text-xs uppercase">Mutator</span>
                            <span className="text-amber-500">{hudState.mutator}</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-emerald-800 text-xs uppercase">Kapital / Habitus</span>
                            <span className="text-zinc-400">{hudState.kapital} | {hudState.habitus}</span>
                        </div>
                    </div>

                    <div className="flex gap-4 items-center bg-black/40 p-2 rounded border border-zinc-800">
                        {/* T-LOAD BAR */}
                        <div className="flex items-center gap-2">
                            <Activity className={hudState.tload > 75 ? "text-red-500 animate-pulse" : "text-emerald-600"} w={16} h={16} />
                            <div className="flex flex-col w-32">
                                <span className="text-[10px] text-zinc-500 uppercase flex justify-between">
                                    <span>T-Load</span>
                                    <span className={hudState.tload > 75 ? "text-red-500" : ""}>{hudState.tload}/100</span>
                                </span>
                                <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                                    <div 
                                        className={`h-full transition-all duration-500 ${hudState.tload > 75 ? 'bg-red-600' : 'bg-amber-500'}`}
                                        style={{ width: \`\${Math.min(hudState.tload, 100)}%\` }}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* RESONANZ BAR */}
                        <div className="flex items-center gap-2">
                            <Cpu className="text-cyan-600" w={16} h={16} />
                            <div className="flex flex-col w-32">
                                <span className="text-[10px] text-zinc-500 uppercase flex justify-between">
                                    <span>Resonanz</span>
                                    <span>{hudState.resonanz}%</span>
                                </span>
                                <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-cyan-600 transition-all duration-500"
                                        style={{ width: \`\${Math.min(hudState.resonanz, 100)}%\` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* MAIN CONTENT */}
            <main className="flex-1 max-w-5xl mx-auto w-full p-4 flex flex-col gap-6 overflow-y-auto pb-32">
                {history.map((entry, idx) => (
                    <div key={idx} className={`flex flex-col ${entry.role === 'user' ? 'items-end' : 'items-start'}`}>
                        {entry.role === 'user' ? (
                            <div className="bg-emerald-900/20 border border-emerald-800 text-emerald-400 px-4 py-2 rounded-lg text-sm mb-4">
                                {entry.content}
                            </div>
                        ) : (
                            <div className="w-full bg-[#0d0d10] border border-zinc-800/80 rounded-xl p-6 shadow-2xl">
                                {entry.imageUrl && (
                                    <div className="mb-6 relative rounded-lg overflow-hidden border-2 border-zinc-800 group">
                                        <div className="absolute top-2 left-2 bg-black/70 backdrop-blur text-xs px-2 py-1 rounded border border-zinc-700 flex items-center gap-2 text-zinc-300 z-10">
                                            <ImageIcon size={12} /> Visueller Feed (Sentinel)
                                        </div>
                                        <img src={entry.imageUrl} alt="Szenerie" className="w-full h-auto object-cover max-h-[600px] opacity-90 group-hover:opacity-100 transition-opacity" />
                                        <div className="absolute inset-0 bg-gradient-to-t from-[#0d0d10] to-transparent opacity-50 pointer-events-none" />
                                    </div>
                                )}
                                <div className="prose prose-invert max-w-none">
                                    {formatAIText(entry.content)}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
                
                {loading && (
                    <div className="flex items-center gap-3 text-emerald-600 animate-pulse bg-emerald-900/10 p-4 rounded-lg self-start w-full border border-emerald-900/30">
                        <Activity className="animate-spin" size={20} />
                        <span className="text-sm font-mono tracking-wider">{loadingMsg}</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </main>

            {/* ACTION CONT
