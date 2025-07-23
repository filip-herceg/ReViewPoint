import {
	ArrowRight,
	BarChart3,
	FileText,
	Shield,
	Sparkles,
	Upload,
	Users,
	Zap,
} from "lucide-react";
import { Link } from "react-router-dom";
import UploadForm from "@/components/UploadForm";
import UploadList from "@/components/UploadList";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { WebSocketStatus } from "@/components/websocket/WebSocketStatus";
import { useAuthStore } from "@/lib/store/authStore";

export default function HomePage() {
	const { isAuthenticated } = useAuthStore();

	return (
		<div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-accent/10">
			{/* Hero Section */}
			<div className="relative overflow-hidden py-24 sm:py-32">
				{/* Background decoration */}
				<div className="absolute inset-0 -z-10 opacity-20">
					<div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-conic from-primary/20 via-accent/10 to-primary/20 rounded-full blur-3xl"></div>
				</div>

				<div className="mx-auto max-w-7xl px-6 lg:px-8">
					<div className="mx-auto max-w-4xl text-center">
						<Badge
							variant="outline"
							className="mb-6 px-3 py-1 text-sm font-medium"
						>
							<Sparkles className="mr-2 h-4 w-4" />
							AI-Powered Document Analysis
						</Badge>

						<h1 className="text-display-xl bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent mb-8 animate-fade-in">
							Transform Your Documents with
							<span className="block text-primary">Intelligent Reviews</span>
						</h1>

						<p className="text-body-lg text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed animate-slide-up">
							Upload your PDF documents and get comprehensive analysis powered
							by advanced AI technology. Get insights, feedback, and actionable
							recommendations in seconds.
						</p>

						{!isAuthenticated && (
							<div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-slide-up">
								<Button asChild size="lg" className="group hover-lift">
									<Link to="/auth/register" className="flex items-center">
										Get Started Free
										<ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
									</Link>
								</Button>
								<Button
									asChild
									variant="outline"
									size="lg"
									className="hover-lift"
								>
									<Link to="/auth/login" className="flex items-center">
										Sign In
									</Link>
								</Button>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* Features Section */}
			<div className="py-24 sm:py-32 bg-gradient-mesh">
				<div className="mx-auto max-w-7xl px-6 lg:px-8">
					<div className="mx-auto max-w-2xl text-center mb-16">
						<h2 className="text-display-lg mb-4">
							Powerful Features for Modern Teams
						</h2>
						<p className="text-body-lg text-muted-foreground">
							Everything you need to analyze, review, and improve your documents
						</p>
					</div>

					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
						{/* Feature Card 1 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
									<Upload className="h-6 w-6 text-primary" />
								</div>
								<CardTitle className="text-xl">Smart Upload</CardTitle>
								<CardDescription className="text-base">
									Drag and drop your PDF files with intelligent file validation
									and processing
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Multiple file support
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Real-time validation
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Progress tracking
									</li>
								</ul>
							</CardContent>
						</Card>

						{/* Feature Card 2 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-success/20 transition-colors">
									<Zap className="h-6 w-6 text-success" />
								</div>
								<CardTitle className="text-xl">AI Analysis</CardTitle>
								<CardDescription className="text-base">
									Advanced AI models analyze your documents for insights and
									recommendations
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-success rounded-full mr-3"></div>
										Content analysis
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-success rounded-full mr-3"></div>
										Quality scoring
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-success rounded-full mr-3"></div>
										Smart suggestions
									</li>
								</ul>
							</CardContent>
						</Card>

						{/* Feature Card 3 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-info/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-info/20 transition-colors">
									<BarChart3 className="h-6 w-6 text-info" />
								</div>
								<CardTitle className="text-xl">Detailed Reports</CardTitle>
								<CardDescription className="text-base">
									Comprehensive reports with scores, feedback, and actionable
									insights
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-info rounded-full mr-3"></div>
										Visual dashboards
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-info rounded-full mr-3"></div>
										Export options
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-info rounded-full mr-3"></div>
										Historical tracking
									</li>
								</ul>
							</CardContent>
						</Card>

						{/* Feature Card 4 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-warning/20 transition-colors">
									<Shield className="h-6 w-6 text-warning" />
								</div>
								<CardTitle className="text-xl">Secure & Private</CardTitle>
								<CardDescription className="text-base">
									Enterprise-grade security with encrypted storage and
									processing
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-warning rounded-full mr-3"></div>
										End-to-end encryption
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-warning rounded-full mr-3"></div>
										GDPR compliant
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-warning rounded-full mr-3"></div>
										Audit trails
									</li>
								</ul>
							</CardContent>
						</Card>

						{/* Feature Card 5 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-destructive/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-destructive/20 transition-colors">
									<Users className="h-6 w-6 text-destructive" />
								</div>
								<CardTitle className="text-xl">Team Collaboration</CardTitle>
								<CardDescription className="text-base">
									Work together with your team on document reviews and analysis
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-destructive rounded-full mr-3"></div>
										Shared workspaces
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-destructive rounded-full mr-3"></div>
										Role-based access
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-destructive rounded-full mr-3"></div>
										Real-time updates
									</li>
								</ul>
							</CardContent>
						</Card>

						{/* Feature Card 6 */}
						<Card className="group hover-lift border-0 shadow-elegant bg-card/80 backdrop-blur-sm">
							<CardHeader className="pb-4">
								<div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
									<FileText className="h-6 w-6 text-primary" />
								</div>
								<CardTitle className="text-xl">Smart Templates</CardTitle>
								<CardDescription className="text-base">
									Pre-built templates for different document types and
									industries
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2 text-sm text-muted-foreground">
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Industry templates
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Custom criteria
									</li>
									<li className="flex items-center">
										<div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
										Template sharing
									</li>
								</ul>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>

			{/* Main Content Based on Auth Status */}
			{isAuthenticated ? (
				<div className="py-24 bg-background">
					<div className="mx-auto max-w-7xl px-6 lg:px-8">
						<div className="flex items-center justify-between mb-12">
							<div>
								<h2 className="text-display-md mb-2">Your Dashboard</h2>
								<p className="text-body-lg text-muted-foreground">
									Manage your documents and track analysis progress
								</p>
							</div>
							<Button asChild size="lg" className="hover-lift">
								<Link to="/uploads/new" className="flex items-center">
									<Upload className="h-4 w-4 mr-2" />
									Upload New File
								</Link>
							</Button>
						</div>

						<div className="grid lg:grid-cols-2 gap-8">
							{/* Upload Form */}
							<Card className="shadow-elegant border-0">
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<Upload className="h-5 w-5" />
										Quick Upload
									</CardTitle>
									<CardDescription>
										Upload a document to get started with AI analysis
									</CardDescription>
								</CardHeader>
								<CardContent>
									<UploadForm />
								</CardContent>
							</Card>

							{/* Recent Files */}
							<Card className="shadow-elegant border-0">
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<FileText className="h-5 w-5" />
										Recent Files
									</CardTitle>
									<CardDescription>
										Your recently uploaded documents
									</CardDescription>
								</CardHeader>
								<CardContent>
									<UploadList />
								</CardContent>
							</Card>
						</div>

						{/* WebSocket Status */}
						<div className="mt-12 p-6 bg-muted/50 rounded-lg border">
							<WebSocketStatus showDetails />
						</div>
					</div>
				</div>
			) : (
				<div className="py-24 bg-gradient-to-t from-muted/30 to-background">
					<div className="mx-auto max-w-4xl px-6 lg:px-8 text-center">
						<Card className="shadow-elegant-lg border-0 bg-card/80 backdrop-blur-sm">
							<CardContent className="p-12">
								<div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-8">
									<Sparkles className="h-8 w-8 text-primary" />
								</div>

								<h2 className="text-display-md mb-6">
									Ready to Transform Your Documents?
								</h2>

								<p className="text-body-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
									Join thousands of teams already using ReViewPoint to analyze,
									review, and improve their documents with AI-powered insights.
								</p>

								<div className="flex flex-col sm:flex-row gap-4 justify-center">
									<Button asChild size="lg" className="hover-lift group">
										<Link to="/auth/register" className="flex items-center">
											Get Started Free
											<ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
										</Link>
									</Button>
									<Button
										asChild
										variant="outline"
										size="lg"
										className="hover-lift"
									>
										<Link to="/auth/login" className="flex items-center">
											Sign In to Your Account
										</Link>
									</Button>
								</div>

								<div className="mt-8 pt-8 border-t border-border/50">
									<p className="text-sm text-muted-foreground">
										No credit card required • Free tier available • Enterprise
										ready
									</p>
								</div>
							</CardContent>
						</Card>
					</div>
				</div>
			)}
		</div>
	);
}
