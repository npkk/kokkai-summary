import { useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { graphqlRequest } from "~/lib/api";
import { SearchContext } from "~/lib/context";
import type { Session } from "~/routes/index/pulldown";
import { MeetingNameDropdown, SessionDropdown } from "~/routes/index/pulldown";
import messages from "~/static/message.json?raw";

// Define types for our data based on the API schema
interface Meeting {
	issueId: string;
	session: number;
	nameOfHouse: string;
	nameOfMeeting: string;
	issue: string;
	date: string;
}

interface Message {
	key: string;
	level: "info" | "warn";
	text: string;
}

const parsedMessages: Message[] | null = (
	JSON.parse(messages) as { messages: Message[] }
).messages;

const bgColor = (msg: Message) => {
	switch (msg.level) {
		case "info":
			return "bg-green-700 dark:bg-green-900";
		case "warn":
			return "bg-yellow-700 dark:bg-yellow-900";
		default:
			return "";
	}
};

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

export default function SearchPage() {
	const [selectedSession, setSelectedSession] = useState<number | null>(null);
	const [selectedMeetingName, setSelectedMeetingName] = useState<string | null>(
		null,
	);
	const [selectedHouses, setSelectedHouses] = useState<string[]>([]);
	const [includeNoSummary, setIncludeNoSummary] = useState(false);

	const [sessions, setSessions] = useState<Session[]>([]);
	const [meetingNames, setMeetingNames] = useState<string[]>([]);
	const [meetings, setMeetings] = useState<Meeting[]>([]);
	const [loading, setLoading] = useState(false);

	const navigate = useNavigate();
	const searchContext = useContext(SearchContext);

	const fetchSessions = useCallback(async () => {
		try {
			const data = await graphqlRequest<{ sessions: Session[] }>(
				GET_SESSIONS_QUERY,
			);
			setSessions(data.sessions);
		} catch (error) {
			console.error("Error fetching sessions:", error);
		}
	}, []);

	const fetchMeetingNames = useCallback(async (session: number) => {
		try {
			const data = await graphqlRequest<{ meetingNames: string[] }>(
				GET_MEETING_NAMES_QUERY,
				{ session: session },
			);
			setMeetingNames(data.meetingNames);
		} catch (error) {
			console.error("Error fetching meeting names:", error);
		}
	}, []);

	const handleSearch = useCallback(
		async (
			session: number | null,
			meetingName: string | null,
			houses: string[],
			includeNoSummary: boolean = false,
		) => {
			if (!session) return;
			setLoading(true);
			try {
				const data = await graphqlRequest<{ meetings: Meeting[] }>(
					SEARCH_MEETINGS_QUERY,
					{
						session: session,
						nameOfMeeting: meetingName,
						nameOfHouse: houses.length === 1 ? houses[0] : null,
						hasSummary: !includeNoSummary,
					},
				);
				setMeetings(data.meetings);
			} catch (error) {
				console.error("Error searching meetings:", error);
			} finally {
				setLoading(false);
			}
		},
		[],
	);

	const handleHouseChange = (house: string) => {
		setSelectedHouses((prev) =>
			prev.includes(house) ? prev.filter((h) => h !== house) : [...prev, house],
		);
	};

	// Fetch sessions
	useEffect(() => {
		fetchSessions();
	}, [fetchSessions]);

	// Fetch meeting names when selectedSession changes
	useEffect(() => {
		if (selectedSession) {
			fetchMeetingNames(selectedSession);
		}
	}, [selectedSession, fetchMeetingNames]);

	// Contextから検索条件を読み込んで検索を実行
	useEffect(() => {
		if (searchContext?.searchCriteria) {
			const { session, nameOfMeeting, nameOfHouse } =
				searchContext.searchCriteria;
			if (session) {
				setSelectedSession(session);
			}
			if (session && nameOfMeeting) {
				setSelectedMeetingName(nameOfMeeting);
			}
			if (nameOfHouse) {
				setSelectedHouses(nameOfHouse);
			}
			handleSearch(session, nameOfMeeting, nameOfHouse);
			searchContext.setSearchCriteria(null);
		}
	}, [searchContext, handleSearch]);

	return (
		<main className="p-4">
			{/* meta */}
			<title>国会会議録要約システム(仮)</title>
			<meta
				name="description"
				content="国会の会議録を要約しているシステムです。"
			/>
			<meta property="og:title" content="国会会議録要約システム(仮)" />
			<meta property="og:locale" content="ja_JP" />
			<meta
				property="og:description"
				content="国会の会議録を要約しているシステムです。"
			/>
			<meta property="og:url" content="https://kokkai-summary.sigsegvvv.xyz" />

			{/* messages */}
			{parsedMessages && (
				<div className="flex flex-col mb-4">
					{parsedMessages.map((msg) => (
						<div
							key={`message-${msg.key}`}
							className={`${bgColor(msg)} text-white rounded my-2`}
						>
							<div className={`p-2 my-1 mx-1 opacity-100`}>{msg.text}</div>
						</div>
					))}
				</div>
			)}

			{/* Session Dropdown */}
			<SessionDropdown
				sessions={sessions}
				selectedSession={selectedSession}
				onSessionChange={setSelectedSession}
			/>

			{/* Meeting Name Dropdown */}

			<MeetingNameDropdown
				meetingNames={meetingNames}
				selectedMeetingName={selectedMeetingName}
				onMeetingNameChange={setSelectedMeetingName}
				disabled={!selectedSession}
			/>

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
									: "bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100"
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
									: "bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-100"
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
							checked={includeNoSummary}
							onChange={(e) => setIncludeNoSummary(e.target.checked)}
						/>
						要約済みでない会議を含める
					</label>
				</div>
			</div>

			{/* Search Button */}
			<button
				type="button"
				onClick={() =>
					handleSearch(
						selectedSession,
						selectedMeetingName,
						selectedHouses,
						includeNoSummary,
					)
				}
				disabled={loading || !selectedSession || !selectedMeetingName}
				className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
			>
				{loading ? "検索中..." : "検索"}
			</button>

			{/* Results */}
			<div className="mt-6">
				{meetings.map((meeting) => (
					<button
						type="button"
						key={meeting.issueId}
						className="border p-4 mb-2 rounded-lg cursor-pointer text-left w-full bg-white dark:bg-gray-800 dark:text-gray-100"
						onClick={() => {
							navigate(`/summary/${meeting.issueId}`);
						}}
					>
						<h2 className="font-bold">{meeting.nameOfMeeting}</h2>
						<p>{meeting.issue}</p>
						<p className="text-sm text-gray-600 dark:text-gray-400">
							{meeting.nameOfHouse} -{" "}
							{new Date(meeting.date).toLocaleDateString()}
						</p>
					</button>
				))}
			</div>
		</main>
	);
}
