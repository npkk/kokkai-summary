import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { graphqlRequest } from "~/lib/api";

// Define types for our data based on the API schema
interface Session {
	session: number;
	name: string;
}

interface Meeting {
	issueId: string;
	session: number;
	nameOfHouse: string;
	nameOfMeeting: string;
	issue: string;
	date: string;
}

// GraphQL Queries (文字列として定義)
const GET_SESSIONS_QUERY = `
  query GetSessions {
    sessions {
      session
      name
    }
  }
`;

const GET_MEETING_NAMES_QUERY = `
  query GetMeetingNames($session: Int!) {
    meetingNames(session: $session)
  }
`;

const SEARCH_MEETINGS_QUERY = `
  query SearchMeetings(
    $session: Int!
    $nameOfHouse: String
    $nameOfMeeting: String
    $hasSummary: Boolean
  ) {
    meetings(
      session: $session
      nameOfHouse: $nameOfHouse
      nameOfMeeting: $nameOfMeeting
      hasSummary: $hasSummary
    ) {
      issueId
      session
      nameOfHouse
      nameOfMeeting
      issue
      date
    }
  }
`;

export function meta() {
	return [
		{ title: "国会会議録検索" },
		{ name: "description", content: "国会会議録の検索" },
	];
}

export default function SearchPage() {
	const [selectedSession, setSelectedSession] = useState<number | null>(null);
	const [selectedMeetingName, setSelectedMeetingName] = useState<string | null>(
		null,
	);
	const [selectedHouses, setSelectedHouses] = useState<string[]>([]);
	const [hasSummary, setHasSummary] = useState(false);

	const [sessions, setSessions] = useState<Session[]>([]);
	const [meetingNames, setMeetingNames] = useState<string[]>([]);
	const [meetings, setMeetings] = useState<Meeting[]>([]);
	const [loading, setLoading] = useState(false);

	const navigate = useNavigate(); // useNavigate を追加

	// Fetch sessions
	useEffect(() => {
		const fetchSessions = async () => {
			try {
				const data = await graphqlRequest<{ sessions: Session[] }>(
					GET_SESSIONS_QUERY,
				);
				setSessions(data.sessions);
				if (data.sessions.length > 0) {
					setSelectedSession(data.sessions[0].session);
				}
			} catch (error) {
				console.error("Error fetching sessions:", error);
			}
		};
		fetchSessions();
	}, []);

	// Fetch meeting names when selectedSession changes
	useEffect(() => {
		const fetchMeetingNames = async () => {
			if (selectedSession) {
				try {
					const data = await graphqlRequest<{ meetingNames: string[] }>(
						GET_MEETING_NAMES_QUERY,
						{ session: selectedSession },
					);
					setMeetingNames(data.meetingNames);
					setSelectedMeetingName(null);
				} catch (error) {
					console.error("Error fetching meeting names:", error);
				}
			}
		};
		fetchMeetingNames();
	}, [selectedSession]);

	const handleSearch = async () => {
		if (!selectedSession) return;
		setLoading(true);
		try {
			const data = await graphqlRequest<{ meetings: Meeting[] }>(
				SEARCH_MEETINGS_QUERY,
				{
					session: selectedSession,
					nameOfMeeting: selectedMeetingName,
					nameOfHouse: selectedHouses.length === 1 ? selectedHouses[0] : null,
											hasSummary: !hasSummary,
				},
			);
			setMeetings(data.meetings);
		} catch (error) {
			console.error("Error searching meetings:", error);
		} finally {
			setLoading(false);
		}
	};

	const handleHouseChange = (house: string) => {
		setSelectedHouses((prev) =>
			prev.includes(house) ? prev.filter((h) => h !== house) : [...prev, house],
		);
	};

	return (
		<div className="p-4 bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100 min-h-screen">
			<h1 className="text-2xl font-bold mb-4">国会会議録検索</h1>

			{/* Session Dropdown */}
			<div className="mb-4">
				<label htmlFor="session-select" className="font-semibold mr-2">
					回次:
				</label>
				<select
					id="session-select"
					value={selectedSession || ""}
					onChange={(e) => setSelectedSession(Number(e.target.value))}
					className="border rounded p-2 bg-white dark:bg-gray-700 dark:text-gray-100"
				>
					{sessions.map((s) => (
						<option key={s.session} value={s.session}>
							{s.name}
						</option>
					))}
				</select>
			</div>

			{/* Meeting Name Dropdown */}
			{selectedSession && (
				<div className="mb-4">
					<label htmlFor="meeting-name-select" className="font-semibold mr-2">
						会議名:
					</label>
					<select
						id="meeting-name-select"
						value={selectedMeetingName || ""}
						onChange={(e) => setSelectedMeetingName(e.target.value)}
						className="border rounded p-2 bg-white dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="">全て</option>
						{meetingNames.map((name) => (
							<option key={name} value={name}>
								{name}
							</option>
						))}
					</select>
				</div>
			)}

			{/* Filters */}
			<div className="flex items-center gap-4 mb-4">
				<div>
					<span className="font-semibold">議院:</span>
					<fieldset className="inline-flex rounded-md shadow-sm ml-2">
						<legend className="font-semibold sr-only">議院:</legend>
						<button
							type="button"
							className={`px-4 py-2 text-sm font-medium border rounded-l-lg ${
								selectedHouses.includes("衆議院")
									? "bg-blue-500 text-white"
									: "bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100" // dark mode styles
							}`}
						onClick={() => handleHouseChange("衆議院")}
						>
							衆議院
						</button>
						<button
							type="button"
							className={`px-4 py-2 text-sm font-medium border-t border-b border-r rounded-r-lg ${
								selectedHouses.includes("参議院")
									? "bg-blue-500 text-white"
									: "bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100" // dark mode styles
							}`}
						onClick={() => handleHouseChange("参議院")}
						>
							参議院
						</button>
					</fieldset>
				</div>
				<div>
					<label>
						<input
							type="checkbox"
							checked={hasSummary}
							onChange={(e) => setHasSummary(e.target.checked)}
						/>{" "}
						要約済みでない会議を含める
					</label>
				</div>
			</div>

			{/* Search Button */}
			<button
				type="button"
				onClick={handleSearch}
				disabled={loading || !selectedSession}
				className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
			>
				{loading ? "検索中..." : "検索"}
			</button>

			{/* Results */}
			<div className="mt-6">
				{meetings.map((meeting) => (
					<button
						type="button" // type="button" を追加
						key={meeting.issueId}
						className="border p-4 mb-2 rounded-lg cursor-pointer text-left w-full bg-white dark:bg-gray-800 dark:text-gray-100" // text-left w-full を追加
						onClick={() => {
							navigate(`/summary/${meeting.issueId}`);
						}} // onClick ハンドラを追加
					>
						<h2 className="font-bold">{meeting.nameOfMeeting}</h2>
						<p>{meeting.issue}</p>
						<p className="text-sm text-gray-600">
							{meeting.nameOfHouse} -{" "}
							{new Date(meeting.date).toLocaleDateString()}
						</p>
					</button>
				))}
			</div>
		</div>
	);
}
